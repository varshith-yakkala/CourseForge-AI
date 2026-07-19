# CourseForge AI — Database Schema Specification

## Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ COURSES : owns
    USERS ||--o{ USER_PROGRESS : tracks
    COURSES ||--o| DOCUMENTS : has
    COURSES ||--o{ LESSONS : contains
    COURSES ||--o{ USER_PROGRESS : tracks
    LESSONS ||--o{ TOPICS : contains
    LESSONS ||--o{ USER_PROGRESS : tracks
    TOPICS ||--o{ SUBTOPICS : contains

    USERS {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        datetime created_at
    }

    COURSES {
        uuid id PK
        uuid owner_id FK
        string title
        text description
        string status
        string difficulty
        integer estimated_duration_min
        array tags
        datetime created_at
    }

    DOCUMENTS {
        uuid id PK
        uuid course_id FK
        string original_filename
        string stored_path
        bigint file_size_bytes
        string mime_type
        string insightforge_doc_id
        string index_status
        integer chunk_count
        datetime created_at
    }

    LESSONS {
        uuid id PK
        uuid course_id FK
        string title
        text summary
        string status
        integer order_index
        integer estimated_duration_min
        text content_markdown
        integer version
        datetime generated_at
        text llm_metadata
    }

    TOPICS {
        uuid id PK
        uuid lesson_id FK
        uuid course_id FK
        string title
        text content
        integer order_index
        array key_terms
    }

    SUBTOPICS {
        uuid id PK
        uuid topic_id FK
        uuid lesson_id FK
        uuid course_id FK
        string title
        text content
        integer order_index
    }

    USER_PROGRESS {
        uuid id PK
        uuid user_id FK
        uuid course_id FK
        uuid lesson_id FK
        string entity_type
        string status
        boolean completed
        integer completion_percentage
        datetime started_at
        datetime completed_at
        datetime last_opened_at
        integer time_spent_sec
    }
```

---

## Model Descriptions & Column Constraints

### `users` Table
- Stores user credentials, hashed passwords (bcrypt), and account state.
- PK: `id` (UUIDv4). Unique index on `email`.

### `courses` Table
- Stores top-level course metadata and generation state.
- `status`: `"processing"`, `"ready"`, `"error"`.

### `documents` Table
- Stores uploaded PDF metadata and InsightForge indexing state.
- `index_status`: `"pending"`, `"processing"`, `"ready"`, `"error"`.

### `lessons` Table
- Stores course lessons, on-demand Markdown text, and generation versions.
- `status`: `"pending"`, `"generating"`, `"ready"`, `"failed"`.
- `version`: Incrementing integer (`1`, `2`, `3`...).

### `user_progress` Table
- Stores user progress metrics per lesson/course across sessions.
- Composite unique index on `(user_id, lesson_id)`.
