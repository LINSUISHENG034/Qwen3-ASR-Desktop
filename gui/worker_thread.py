"""
Worker Thread for Qwen3-ASR GUI
Handles async transcription processing with progress signals
"""

import os
import traceback
from datetime import timedelta
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QThread, pyqtSignal

try:
    import srt
    import dashscope
    from silero_vad import load_silero_vad

    from qwen3_asr_toolkit.qwen3asr import QwenASR
    from qwen3_asr_toolkit.audio_tools import (
        load_audio,
        process_vad,
        save_audio_file,
        WAV_SAMPLE_RATE,
    )
except ImportError as e:
    print(f"Import error: {e}")


class TranscriptionWorker(QThread):
    """Worker thread for non-blocking transcription processing."""

    # Signals
    progress = pyqtSignal(int, int, str)  # current, total, message
    segment_completed = pyqtSignal(int, str, float, float)  # idx, text, start, end
    finished_transcription = pyqtSignal(str, str, list)  # full_text, language, segments
    error = pyqtSignal(str)  # error message
    status_update = pyqtSignal(str)  # status text

    def __init__(
        self,
        input_file: str,
        api_key: str,
        num_threads: int = 4,
        vad_threshold: int = 120,
        context: str = "",
        save_srt: bool = False,
        tmp_dir: Optional[str] = None,
    ):
        super().__init__()
        self.input_file = input_file
        self.api_key = api_key
        self.num_threads = num_threads
        self.vad_threshold = vad_threshold
        self.context = context
        self.save_srt = save_srt
        self.tmp_dir = tmp_dir or os.path.join(os.path.expanduser("~"), "qwen3-asr-cache")
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation of the transcription."""
        self._is_cancelled = True

    def run(self):
        """Execute the transcription pipeline."""
        try:
            # Set API key
            if self.api_key:
                dashscope.api_key = self.api_key
            elif "DASHSCOPE_API_KEY" not in os.environ:
                self.error.emit("No API key provided. Please set DASHSCOPE_API_KEY or enter it in settings.")
                return

            self.status_update.emit("Loading audio file...")
            self.progress.emit(0, 100, "Loading audio...")

            if self._is_cancelled:
                return

            # Load audio
            wav = load_audio(self.input_file)
            duration = len(wav) / WAV_SAMPLE_RATE
            self.status_update.emit(f"Loaded audio: {duration:.1f}s")
            self.progress.emit(10, 100, f"Audio loaded ({duration:.1f}s)")

            if self._is_cancelled:
                return

            # Segment if needed
            if duration >= 180:
                self.status_update.emit("Initializing VAD for segmenting...")
                self.progress.emit(15, 100, "Loading VAD model...")
                worker_vad_model = load_silero_vad(onnx=True)
                wav_list = process_vad(wav, worker_vad_model, segment_threshold_s=self.vad_threshold)
                self.status_update.emit(f"Segmented into {len(wav_list)} chunks")
                self.progress.emit(20, 100, f"Split into {len(wav_list)} segments")
            else:
                wav_list = [(0, len(wav), wav)]

            if self._is_cancelled:
                return

            # Prepare temp files
            wav_name = os.path.basename(self.input_file)
            wav_dir_name = os.path.splitext(wav_name)[0]
            save_dir = os.path.join(self.tmp_dir, wav_dir_name)

            wav_path_list = []
            for idx, (_, _, wav_data) in enumerate(wav_list):
                wav_path = os.path.join(save_dir, f"{wav_name}_{idx}.wav")
                save_audio_file(wav_data, wav_path)
                wav_path_list.append(wav_path)

            self.progress.emit(25, 100, "Starting transcription...")

            if self._is_cancelled:
                self._cleanup(save_dir)
                return

            # Process segments
            qwen3asr = QwenASR(model="qwen3-asr-flash")
            results = []
            languages = []
            total_segments = len(wav_path_list)

            import concurrent.futures
            from collections import Counter

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                future_dict = {
                    executor.submit(qwen3asr.asr, wav_path, self.context): idx
                    for idx, wav_path in enumerate(wav_path_list)
                }

                completed = 0
                for future in concurrent.futures.as_completed(future_dict):
                    if self._is_cancelled:
                        executor.shutdown(wait=False, cancel_futures=True)
                        self._cleanup(save_dir)
                        return

                    idx = future_dict[future]
                    try:
                        language, recog_text = future.result()
                        results.append((idx, recog_text))
                        languages.append(language)

                        # Emit segment completion
                        start_time = wav_list[idx][0] / WAV_SAMPLE_RATE
                        end_time = wav_list[idx][1] / WAV_SAMPLE_RATE
                        self.segment_completed.emit(idx, recog_text, start_time, end_time)

                        completed += 1
                        progress_pct = 25 + int((completed / total_segments) * 70)
                        self.progress.emit(progress_pct, 100, f"Transcribed {completed}/{total_segments}")
                        self.status_update.emit(f"Processing segment {completed}/{total_segments}")
                    except Exception as e:
                        self.error.emit(f"Segment {idx} failed: {str(e)}")

            # Sort and combine results
            results.sort(key=lambda x: x[0])
            full_text = " ".join(text for _, text in results)
            detected_language = Counter(languages).most_common(1)[0][0] if languages else "Unknown"

            self.progress.emit(95, 100, "Finalizing...")

            # Build segments list for SRT
            segments = []
            for idx, (_, text) in enumerate(results):
                start_time = wav_list[idx][0] / WAV_SAMPLE_RATE
                end_time = wav_list[idx][1] / WAV_SAMPLE_RATE
                segments.append({
                    "index": idx,
                    "start": start_time,
                    "end": end_time,
                    "text": text,
                })

            # Save output files
            if os.path.exists(self.input_file):
                base_path = os.path.splitext(self.input_file)[0]
            else:
                from urllib.parse import urlparse
                base_path = os.path.splitext(urlparse(self.input_file).path)[0].split("/")[-1]

            # Save TXT
            txt_path = base_path + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"{detected_language}\n")
                f.write(f"{full_text}\n")

            # Save SRT if requested
            if self.save_srt:
                srt_path = base_path + ".srt"
                subtitles = []
                for seg in segments:
                    subtitles.append(
                        srt.Subtitle(
                            index=seg["index"],
                            start=timedelta(seconds=seg["start"]),
                            end=timedelta(seconds=seg["end"]),
                            content=seg["text"],
                        )
                    )
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt.compose(subtitles))

            # Cleanup
            self._cleanup(save_dir)

            self.progress.emit(100, 100, "Complete!")
            self.status_update.emit(f"Transcription complete • {detected_language}")
            self.finished_transcription.emit(full_text, detected_language, segments)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(f"Transcription failed: {str(e)}")

    def _cleanup(self, save_dir: str):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(save_dir):
                shutil.rmtree(save_dir)
        except Exception:
            pass


class BatchTranscriptionWorker(QThread):
    """Worker thread for batch transcription of multiple files."""

    # Per-file signals
    file_started = pyqtSignal(int, str)  # file_idx, filename
    file_progress = pyqtSignal(int, int, int, str)  # file_idx, current%, total%, message
    file_completed = pyqtSignal(int, str, str, list)  # file_idx, full_text, language, segments
    file_error = pyqtSignal(int, str)  # file_idx, error message

    # Batch signals
    batch_progress = pyqtSignal(int, int)  # completed_files, total_files
    batch_finished = pyqtSignal(list)  # list of all results

    def __init__(
        self,
        input_files: List[str],
        api_key: str,
        num_threads: int = 4,
        vad_threshold: int = 120,
        context: str = "",
        save_srt: bool = False,
        tmp_dir: Optional[str] = None,
    ):
        super().__init__()
        self.input_files = input_files
        self.api_key = api_key
        self.num_threads = num_threads
        self.vad_threshold = vad_threshold
        self.context = context
        self.save_srt = save_srt
        self.tmp_dir = tmp_dir or os.path.join(os.path.expanduser("~"), "qwen3-asr-cache")
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation of the batch transcription."""
        self._is_cancelled = True

    def run(self):
        """Execute batch transcription pipeline."""
        results = []
        total_files = len(self.input_files)

        for file_idx, input_file in enumerate(self.input_files):
            if self._is_cancelled:
                break

            filename = os.path.basename(input_file)
            self.file_started.emit(file_idx, filename)

            try:
                result = self._process_single_file(file_idx, input_file, total_files)
                results.append(result)
                self.file_completed.emit(
                    file_idx,
                    result["full_text"],
                    result["language"],
                    result["segments"],
                )
            except Exception as e:
                traceback.print_exc()
                self.file_error.emit(file_idx, str(e))
                results.append({
                    "file_idx": file_idx,
                    "input_file": input_file,
                    "error": str(e),
                    "full_text": "",
                    "language": "",
                    "segments": [],
                })

            self.batch_progress.emit(file_idx + 1, total_files)

        self.batch_finished.emit(results)

    def _process_single_file(
        self, file_idx: int, input_file: str, total_files: int
    ) -> Dict[str, Any]:
        """Process a single file and return results."""
        # Set API key
        if self.api_key:
            dashscope.api_key = self.api_key
        elif "DASHSCOPE_API_KEY" not in os.environ:
            raise ValueError("No API key provided")

        self.file_progress.emit(file_idx, 0, 100, "Loading audio...")

        if self._is_cancelled:
            raise InterruptedError("Cancelled")

        # Load audio
        wav = load_audio(input_file)
        duration = len(wav) / WAV_SAMPLE_RATE
        self.file_progress.emit(file_idx, 10, 100, f"Audio loaded ({duration:.1f}s)")

        if self._is_cancelled:
            raise InterruptedError("Cancelled")

        # Segment if needed
        if duration >= 180:
            self.file_progress.emit(file_idx, 15, 100, "Loading VAD model...")
            worker_vad_model = load_silero_vad(onnx=True)
            wav_list = process_vad(wav, worker_vad_model, segment_threshold_s=self.vad_threshold)
            self.file_progress.emit(file_idx, 20, 100, f"Split into {len(wav_list)} segments")
        else:
            wav_list = [(0, len(wav), wav)]

        if self._is_cancelled:
            raise InterruptedError("Cancelled")

        # Prepare temp files
        wav_name = os.path.basename(input_file)
        wav_dir_name = os.path.splitext(wav_name)[0]
        save_dir = os.path.join(self.tmp_dir, wav_dir_name)

        wav_path_list = []
        for idx, (_, _, wav_data) in enumerate(wav_list):
            wav_path = os.path.join(save_dir, f"{wav_name}_{idx}.wav")
            save_audio_file(wav_data, wav_path)
            wav_path_list.append(wav_path)

        self.file_progress.emit(file_idx, 25, 100, "Starting transcription...")

        if self._is_cancelled:
            self._cleanup(save_dir)
            raise InterruptedError("Cancelled")

        # Process segments
        return self._transcribe_segments(
            file_idx, input_file, wav_list, wav_path_list, save_dir
        )

    def _transcribe_segments(
        self,
        file_idx: int,
        input_file: str,
        wav_list: list,
        wav_path_list: list,
        save_dir: str,
    ) -> Dict[str, Any]:
        """Transcribe audio segments and return combined results."""
        import concurrent.futures
        from collections import Counter

        qwen3asr = QwenASR(model="qwen3-asr-flash")
        results = []
        languages = []
        total_segments = len(wav_path_list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            future_dict = {
                executor.submit(qwen3asr.asr, wav_path, self.context): idx
                for idx, wav_path in enumerate(wav_path_list)
            }

            completed = 0
            for future in concurrent.futures.as_completed(future_dict):
                if self._is_cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    self._cleanup(save_dir)
                    raise InterruptedError("Cancelled")

                idx = future_dict[future]
                language, recog_text = future.result()
                results.append((idx, recog_text))
                languages.append(language)

                completed += 1
                progress_pct = 25 + int((completed / total_segments) * 70)
                self.file_progress.emit(
                    file_idx, progress_pct, 100,
                    f"Transcribed {completed}/{total_segments}"
                )

        # Sort and combine results
        results.sort(key=lambda x: x[0])
        full_text = " ".join(text for _, text in results)
        detected_language = Counter(languages).most_common(1)[0][0] if languages else "Unknown"

        self.file_progress.emit(file_idx, 95, 100, "Finalizing...")

        # Build segments list
        segments = []
        for idx, (_, text) in enumerate(results):
            start_time = wav_list[idx][0] / WAV_SAMPLE_RATE
            end_time = wav_list[idx][1] / WAV_SAMPLE_RATE
            segments.append({
                "index": idx,
                "start": start_time,
                "end": end_time,
                "text": text,
            })

        # Save output files
        self._save_output_files(input_file, full_text, detected_language, segments)

        # Cleanup temp files
        self._cleanup(save_dir)

        self.file_progress.emit(file_idx, 100, 100, "Complete!")

        return {
            "file_idx": file_idx,
            "input_file": input_file,
            "full_text": full_text,
            "language": detected_language,
            "segments": segments,
            "error": None,
        }

    def _save_output_files(
        self,
        input_file: str,
        full_text: str,
        detected_language: str,
        segments: list,
    ):
        """Save transcription results to TXT and optionally SRT files."""
        if os.path.exists(input_file):
            base_path = os.path.splitext(input_file)[0]
        else:
            from urllib.parse import urlparse
            base_path = os.path.splitext(urlparse(input_file).path)[0].split("/")[-1]

        # Save TXT
        txt_path = base_path + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{detected_language}\n")
            f.write(f"{full_text}\n")

        # Save SRT if requested
        if self.save_srt and segments:
            srt_path = base_path + ".srt"
            subtitles = []
            for seg in segments:
                subtitles.append(
                    srt.Subtitle(
                        index=seg["index"],
                        start=timedelta(seconds=seg["start"]),
                        end=timedelta(seconds=seg["end"]),
                        content=seg["text"],
                    )
                )
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt.compose(subtitles))

    def _cleanup(self, save_dir: str):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(save_dir):
                shutil.rmtree(save_dir)
        except Exception:
            pass
