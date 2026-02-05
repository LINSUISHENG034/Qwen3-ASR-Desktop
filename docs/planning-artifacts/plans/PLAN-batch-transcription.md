# Implementation Plan: Batch File Transcription for Qwen3-ASR GUI

## Overview
Enhance `run_gui.py` and related GUI components to support selecting and transcribing multiple files from a folder, instead of only single file selection.

## Current State Analysis

### Existing Architecture
- **`run_gui.py`**: Entry point, launches `MainWindow`
- **`gui/main_window.py`**:
  - `DropZone`: Handles single file drag-drop (only takes first URL)
  - `_browse_file()`: Uses `QFileDialog.getOpenFileName()` (single file)
  - `current_file`: Stores single file path
  - `TranscriptionWorker`: Processes single file
- **`gui/worker_thread.py`**: `TranscriptionWorker` handles one file at a time
- **`gui/transcription_panel.py`**: Displays results for single transcription

### Key Constraints
- Worker thread processes one file sequentially
- UI shows progress for single file
- Results panel designed for single file output

---

## Implementation Steps

### Step 1: Update DropZone for Multiple Files
**File**: `gui/main_window.py`

Changes:
- Modify `file_dropped` signal to emit `list[str]` instead of `str`
- Update `dropEvent()` to collect all valid files from dropped URLs
- Update `set_file()` to display file count when multiple files selected
- Add `set_files()` method for batch display

### Step 2: Add Multi-File Browse Dialog
**File**: `gui/main_window.py`

Changes:
- Replace `QFileDialog.getOpenFileName()` with `QFileDialog.getOpenFileNames()`
- Add new "Browse Folder" button using `QFileDialog.getExistingDirectory()`
- Store `current_files: List[str]` instead of single `current_file`

### Step 3: Create File Queue Widget
**File**: `gui/main_window.py` (new widget class)

New component `FileQueueWidget`:
- `QListWidget` showing selected files with checkboxes
- Select/deselect individual files
- Remove files from queue
- Show file size and status (pending/processing/done/error)
- "Select All" / "Deselect All" buttons

### Step 4: Create Batch Worker Thread
**File**: `gui/worker_thread.py`

New class `BatchTranscriptionWorker(QThread)`:
- Accept `List[str]` of input files
- New signals:
  - `file_started(int, str)` - file index, filename
  - `file_progress(int, int, int, str)` - file_idx, current, total, message
  - `file_completed(int, str, str, list)` - file_idx, full_text, language, segments
  - `file_error(int, str)` - file_idx, error message
  - `batch_progress(int, int)` - completed_files, total_files
  - `batch_finished(list)` - list of results
- Process files sequentially (reuse existing single-file logic)
- Support cancellation at file boundaries

### Step 5: Update Transcription Panel for Batch Results
**File**: `gui/transcription_panel.py`

Changes:
- Add tabbed interface or accordion for multiple file results
- Each file gets its own result section
- Batch export: "Export All as TXT", "Export All as SRT"
- Summary view showing all files and their status

### Step 6: Update MainWindow for Batch Mode
**File**: `gui/main_window.py`

Changes:
- Replace `current_file` with `current_files: List[str]`
- Add file queue widget to UI layout
- Update `_start_transcription()` to use `BatchTranscriptionWorker`
- Update progress bar to show overall batch progress
- Add per-file progress indicator
- Update stats sidebar to show batch statistics

### Step 7: Update UI Layout
**File**: `gui/main_window.py`

Layout changes:
- Expand input card to include file queue
- Add "Browse Files" and "Browse Folder" buttons
- Show batch progress (e.g., "Processing 3/10 files")

---

## Detailed Component Changes

### DropZone Changes
```python
# Signal change
files_dropped = pyqtSignal(list)  # List[str]

# dropEvent change
def dropEvent(self, event):
    urls = event.mimeData().urls()
    valid_files = [
        url.toLocalFile() for url in urls
        if self._is_supported_file(url.toLocalFile())
    ]
    if valid_files:
        self.files_dropped.emit(valid_files)
```

### Browse Methods
```python
def _browse_files(self):
    """Open multi-file browser dialog."""
    file_paths, _ = QFileDialog.getOpenFileNames(...)
    if file_paths:
        self._on_files_selected(file_paths)

def _browse_folder(self):
    """Open folder browser and select all media files."""
    folder = QFileDialog.getExistingDirectory(...)
    if folder:
        files = self._scan_folder_for_media(folder)
        if files:
            self._on_files_selected(files)
```

### FileQueueWidget Structure
```python
class FileQueueWidget(QWidget):
    files_changed = pyqtSignal(list)  # Emitted when selection changes

    def __init__(self):
        self.file_list = QListWidget()
        # Checkboxes for each file
        # Status icons (pending/processing/done/error)

    def add_files(self, file_paths: List[str])
    def remove_selected(self)
    def get_selected_files(self) -> List[str]
    def set_file_status(self, index: int, status: str)
    def clear(self)
```

### BatchTranscriptionWorker Signals
```python
class BatchTranscriptionWorker(QThread):
    # Per-file signals
    file_started = pyqtSignal(int, str)  # idx, filename
    file_progress = pyqtSignal(int, int, int, str)  # file_idx, current%, total%, msg
    file_completed = pyqtSignal(int, str, str, list)  # idx, text, lang, segments
    file_error = pyqtSignal(int, str)  # idx, error

    # Batch signals
    batch_progress = pyqtSignal(int, int)  # completed, total
    batch_finished = pyqtSignal(list)  # all results
```

---

## UI Mockup (Text)

```
┌─────────────────────────────────────────────────────────────────┐
│ ✨ Qwen3-ASR                                                    │
│ Toolkit v1.0                                                    │
│                                                                 │
│ [🎙️ Transcribe]  ← selected                                    │
│ [⚙️ Settings]                                                   │
│                                                                 │
│ ┌─────────────┐                                                 │
│ │ 📊 Stats    │                                                 │
│ │ 5 files     │                                                 │
│ │ 3 done      │                                                 │
│ │ 1 processing│                                                 │
│ │ 1 pending   │                                                 │
│ └─────────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Audio Transcription                                             │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  🎵 Drag & Drop Files or Folder Here                        │ │
│ │     or click buttons below                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [📂 Browse Files] [📁 Browse Folder]                            │
│                                                                 │
│ ┌─ File Queue ────────────────────────────────────────────────┐ │
│ │ ☑ audio1.mp3      12.5 MB   ✅ Done                         │ │
│ │ ☑ audio2.wav       8.2 MB   ✅ Done                         │ │
│ │ ☑ video1.mp4      45.0 MB   ✅ Done                         │ │
│ │ ☑ audio3.m4a       5.1 MB   🔄 Processing... 45%            │ │
│ │ ☑ audio4.flac     22.3 MB   ⏳ Pending                      │ │
│ │ ☐ audio5.ogg       3.2 MB   ⏳ Pending (unchecked)          │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ [Select All] [Deselect All] [Remove Selected]               │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Overall: ████████████░░░░░░░░ 60% (3/5 files)                   │
│                                                                 │
│ [✖ Cancel]                              [🚀 Transcribe Selected]│
├─────────────────────────────────────────────────────────────────┤
│ Transcription Results                              🌐 Chinese   │
│ ┌─ Tabs ──────────────────────────────────────────────────────┐ │
│ │ [audio1.mp3] [audio2.wav] [video1.mp4] [Summary]            │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ [00:00.000 → 00:15.234]                                     │ │
│ │ 这是第一段转录文本...                                        │ │
│ │                                                             │ │
│ │ [00:15.234 → 00:32.567]                                     │ │
│ │ 这是第二段转录文本...                                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ✓ Complete • 3 files done    [📋 Copy] [💾 Save TXT] [🎬 SRT]  │
│                              [📦 Export All]                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Changes Summary

| File | Changes |
|------|---------|
| `gui/main_window.py` | Major: DropZone multi-file, FileQueueWidget, batch UI |
| `gui/worker_thread.py` | Add `BatchTranscriptionWorker` class |
| `gui/transcription_panel.py` | Add tabbed results, batch export |
| `run_gui.py` | No changes needed |

---

## Testing Checklist

- [ ] Single file drag-drop still works
- [ ] Multiple file drag-drop works
- [ ] Browse Files dialog allows multi-select
- [ ] Browse Folder scans and adds all media files
- [ ] File queue shows correct status icons
- [ ] Checkbox selection/deselection works
- [ ] Remove selected files works
- [ ] Batch transcription processes files sequentially
- [ ] Per-file progress updates correctly
- [ ] Overall batch progress updates correctly
- [ ] Cancel stops at file boundary
- [ ] Results tabs show per-file transcriptions
- [ ] Export All exports all completed files
- [ ] Error handling for individual file failures
- [ ] Memory cleanup after batch completion

---

## Implementation Order

1. **Step 4**: Create `BatchTranscriptionWorker` (can test independently)
2. **Step 3**: Create `FileQueueWidget` (can test independently)
3. **Step 1**: Update `DropZone` for multiple files
4. **Step 2**: Add multi-file browse dialogs
5. **Step 6**: Update `MainWindow` to wire everything together
6. **Step 5**: Update `TranscriptionPanel` for batch results
7. **Step 7**: Final UI polish and layout adjustments

---

## Acceptance Criteria

### Functional Requirements
- [ ] Batch mode supports 1-100+ files without crashes
- [ ] Single file mode works identically to before (backward compatible)
- [ ] All existing file formats supported in batch mode
- [ ] Partial batch completion saves completed results

### Performance Requirements
- [ ] Memory usage stays reasonable for large batches (files processed sequentially)
- [ ] UI remains responsive during batch processing
- [ ] Progress updates at least every 2 seconds per file

### User Experience
- [ ] Clear visual feedback for each file's status
- [ ] Easy to add/remove files from queue before processing
- [ ] Batch can be cancelled cleanly at file boundaries

---

## Error Handling Strategy

### Individual File Failures
- **Behavior**: If one file fails, batch continues with remaining files
- **UI Feedback**: Failed file shows ❌ icon with error tooltip
- **Logging**: Error details logged to console/log file

### Failure Scenarios
| Scenario | Handling |
|----------|----------|
| File not found | Skip, mark as error, continue batch |
| Unsupported format | Skip, mark as error, continue batch |
| Corrupted audio | Skip, mark as error, continue batch |
| Out of memory | Stop batch, save completed results, show warning |
| User cancellation | Stop at current file boundary, keep completed results |

### Result Reporting
- Summary shows: `✅ 8 succeeded, ❌ 2 failed`
- Failed files listed with error reasons
- Completed transcriptions still exportable

---

## Configuration Options

### Default Behavior (No Config Required)
- No maximum file limit (user's responsibility)
- Sequential processing (one file at a time)
- Results stored in memory until export

### Export Options
- **Export All as TXT**: One file per transcription, or combined
- **Export All as SRT**: One SRT file per source file
- **Output Directory**: Same as source file by default

---

## Risks and Considerations

| Risk | Mitigation |
|------|------------|
| Large batch exhausts memory | Sequential processing, clear results after export |
| Long-running batch blocks UI | Worker thread with progress signals |
| User adds files during processing | Disable add/remove while batch running |
| Mixed file quality in batch | Per-file error handling, don't fail entire batch |

---

## Dependencies

- **PyQt6**: No new dependencies, uses existing `QThread`, `QListWidget`, `QTabWidget`
- **Existing code**: Reuses `TranscriptionWorker` logic internally
- **No breaking changes**: All existing single-file APIs preserved
