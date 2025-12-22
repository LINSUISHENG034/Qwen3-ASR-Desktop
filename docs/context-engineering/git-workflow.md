## Git Workflow

### Branch Strategy

We follow a structured branching model to ensure stability and parallel development:

- `main` - Production-ready code. Protected branch.
- `develop` - Integration branch for features (if applicable).
- `feature/<name>` - New features. Created from `main` or `develop`.
- `fix/<name>` - Bug fixes. Created from `main`.
- `hotfix/<name>` - Critical production fixes.
- `docs/<name>` - Documentation updates.
- `refactor/<name>` - Code refactoring.
- `test/<name>` - Test additions or fixes.

### Commit Message Convention

We adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification to ensure readable and machine-parsable commit history.

**Crucial Rule:** Never include "written by claude" or AI-generation disclaimers in commit messages.

#### Message Structure

```text
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

#### 1. Header

The header is mandatory and must be formatted as follows:

**Type**

Must be one of the following:

| Type | Description | Emoji (Optional) |
| :--- | :--- | :--- |
| `feat` | A new feature | ✨ |
| `fix` | A bug fix | 🐛 |
| `docs` | Documentation only changes | 📚 |
| `style` | Changes that do not affect the meaning of the code (white-space, formatting, etc) | 💎 |
| `refactor` | A code change that neither fixes a bug nor adds a feature | ♻️ |
| `perf` | A code change that improves performance | 🚀 |
| `test` | Adding missing tests or correcting existing tests | 🚨 |
| `build` | Changes that affect the build system or external dependencies | 🛠️ |
| `ci` | Changes to our CI configuration files and scripts | ⚙️ |
| `chore` | Other changes that don't modify src or test files | 🧹 |
| `revert` | Reverts a previous commit | ⏪ |

**Scope** (Optional)

The scope provides additional context:
- `api`, `auth`, `db`, `core`, `deps`, `ui`
- Example: `feat(auth): add login endpoint`

**Subject**

- Use **imperative, present tense**: "change" not "changed" nor "changes".
- **No dot** (`.`) at the end.
- Limit to **50 characters** if possible.
- Concise description of *what* happened.

#### 2. Body (Optional)

- Use imperative, present tense.
- Include the **motivation** for the change and contrast with previous behavior.
- Wrap lines at 72 characters.

#### 3. Footer (Optional)

- **BREAKING CHANGE**: Start with `BREAKING CHANGE:` followed by a description.
- **Referencing Issues**: `Closes #123`, `Fixes #42`.

#### Examples

**Feature with Body and Footer:**
```text
feat(auth): add two-factor authentication

Implement TOTP generation and validation using the pyotp library.
Add QR code generation endpoint for authenticator apps.

Closes #123
```

**Breaking Change:**
```text
refactor(api): switch to GraphQL

BREAKING CHANGE: The REST API endpoints are removed in favor of GraphQL.
```

**Documentation:**
```text
docs(readme): update installation instructions
```

## Database Naming Standards

### Entity-Specific Primary Keys
All database tables use entity-specific primary keys for clarity and consistency:

```sql
-- STANDARDIZED: Entity-specific primary keys
sessions.session_id UUID PRIMARY KEY
leads.lead_id UUID PRIMARY KEY
messages.message_id UUID PRIMARY KEY
daily_metrics.daily_metric_id UUID PRIMARY KEY
agencies.agency_id UUID PRIMARY KEY
```

### Field Naming Conventions

```sql
-- Primary keys: {entity}_id
session_id, lead_id, message_id

-- Foreign keys: {referenced_entity}_id
session_id REFERENCES sessions(session_id)
agency_id REFERENCES agencies(agency_id)

-- Timestamps: {action}_at
created_at, updated_at, started_at, expires_at

-- Booleans: is_{state}
is_connected, is_active, is_qualified

-- Counts: {entity}_count
message_count, lead_count, notification_count

-- Durations: {property}_{unit}
duration_seconds, timeout_minutes
```

### Repository Pattern Auto-Derivation

The enhanced BaseRepository automatically derives table names and primary keys:

```python
# STANDARDIZED: Convention-based repositories
class LeadRepository(BaseRepository[Lead]):
    def __init__(self):
        super().__init__()  # Auto-derives "leads" and "lead_id"

class SessionRepository(BaseRepository[AvatarSession]):
    def __init__(self):
        super().__init__()  # Auto-derives "sessions" and "session_id"
```

**Benefits**:

- Self-documenting schema
- Clear foreign key relationships
- Eliminates repository method overrides
- Consistent with entity naming patterns

### Model-Database Alignment

Models mirror database fields exactly to eliminate field mapping complexity:

```python
# STANDARDIZED: Models mirror database exactly
class Lead(BaseModel):
    lead_id: UUID = Field(default_factory=uuid4)  # Matches database field
    session_id: UUID                               # Matches database field
    agency_id: str                                 # Matches database field
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        alias_generator=None  # Use exact field names
    )
```

### API Route Standards

```python
# STANDARDIZED: RESTful with consistent parameter naming
router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

@router.get("/{lead_id}")           # GET /api/v1/leads/{lead_id}
@router.put("/{lead_id}")           # PUT /api/v1/leads/{lead_id}
@router.delete("/{lead_id}")        # DELETE /api/v1/leads/{lead_id}

# Sub-resources
@router.get("/{lead_id}/messages")  # GET /api/v1/leads/{lead_id}/messages
@router.get("/agency/{agency_id}")  # GET /api/v1/leads/agency/{agency_id}
```

For complete naming standards, see [NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md).