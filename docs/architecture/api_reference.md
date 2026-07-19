# CourseForge AI — API Reference Specification

Base API Path: `/api/v1`

---

## 1. Authentication Endpoints (`/auth`)

### `POST /auth/register`
Registers a new user account.
- **Request Body**: `{ "email": "user@example.com", "password": "password123", "full_name": "Jane Doe" }`
- **Response**: `201 Created` — `UserResponse`

### `POST /auth/login`
Authenticates credentials and returns JWT bearer tokens.
- **Request Body**: `{ "email": "user@example.com", "password": "password123" }`
- **Response**: `200 OK` — `{ "access_token": "...", "refresh_token": "...", "expires_in": 86400 }`

---

## 2. Course Endpoints (`/courses`)

### `GET /courses`
Lists all courses owned by the authenticated user.
- **Response**: `200 OK` — `List[CourseResponse]`

### `POST /courses`
Creates a new course entity.
- **Request Body**: `{ "title": "Machine Learning 101", "description": "Intro course" }`
- **Response**: `201 Created` — `CourseResponse`

### `POST /courses/{id}/generate`
Triggers course blueprint generation (Lessons ➔ Topics ➔ Subtopics).
- **Response**: `200 OK` — `CourseResponse`

### `GET /courses/{id}/structure`
Fetches complete nested course syllabus tree.
- **Response**: `200 OK` — `{ "course_id": "...", "lessons": [...] }`

---

## 3. Document Endpoints (`/documents`)

### `POST /documents/upload`
Uploads a PDF file and enqueues Celery indexing.
- **Form Data**: `course_id` (UUID), `file` (Binary PDF file)
- **Response**: `202 Accepted` — `DocumentResponse`

---

## 4. Lesson & Learning Endpoints (`/courses/{course_id}/lessons`)

### `GET /courses/{course_id}/lessons/{lesson_id}`
Retrieves lesson details. Automatically triggers on-demand generation if status is `pending`.
- **Response**: `200 OK` — `LessonDetailResponse`

### `POST /courses/{course_id}/lessons/{lesson_id}/generate`
Generates lesson Markdown content.
- **Response**: `200 OK` — `LessonDetailResponse`

### `POST /courses/{course_id}/lessons/{lesson_id}/regenerate`
Force regenerates lesson content and increments `version`.
- **Response**: `200 OK` — `LessonDetailResponse`

### `POST /courses/{course_id}/lessons/{lesson_id}/progress`
Updates user progress metrics for the lesson.
- **Request Body**: `{ "status": "completed", "completed": true, "completion_percentage": 100, "time_spent_sec": 120 }`
- **Response**: `200 OK` — `ProgressResponse`

### `GET /courses/{course_id}/progress`
Retrieves course progress overview (total lessons, completed lessons, overall percentage).
- **Response**: `200 OK` — `CourseProgressOverview`

### `POST /courses/{course_id}/lessons/{lesson_id}/ask`
Asks a question to the AI tutor scoped strictly to the current lesson context.
- **Request Body**: `{ "question": "Explain this concept in simple terms" }`
- **Response**: `200 OK` — `{ "answer": "...", "lesson_id": "..." }`
