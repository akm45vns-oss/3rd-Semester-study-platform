# Database Schema Documentation — Semester OS

The database contains **22 SQLAlchemy relational tables** organized into 4 functional domains.

---

## 1. Curriculum Domain

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `subjects` | 5 official semester subjects | `id`, `course_code` (UNIQUE), `name`, `credits`, `sort_order` |
| `units` | 30 curriculum units (6 per subject) | `id`, `subject_id` (FK), `unit_number` (1-6), `name` |
| `topics` | Syllabus topics within units | `id`, `unit_id` (FK), `name`, `source_type`, `has_coding` |
| `subtopics` | Granular sub-concepts | `id`, `topic_id` (FK), `name`, `sort_order` |
| `course_outcomes`| Official CO statements | `id`, `subject_id` (FK), `outcome_code`, `description` |
| `practicals` | Official syllabus laboratory experiments | `id`, `subject_id` (FK), `practical_number`, `title` |

---

## 2. Practice & Assessment Domain

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `questions` | Question bank items | `id`, `topic_id` (FK), `question_text`, `question_type`, `difficulty`, `explanation` |
| `question_options`| Options for questions | `id`, `question_id` (FK), `option_text`, `is_correct`, `sort_order` |
| `practice_attempts`| User attempt logs & score | `id`, `user_id` (FK), `question_id` (FK), `is_correct`, `score`, `session_id` |
| `coding_problems` | Coding/SQL challenge specs | `id`, `topic_id` (FK), `title`, `language`, `starter_code`, `expected_output` |
| `coding_submissions` | User code submissions | `id`, `user_id` (FK), `problem_id` (FK), `code`, `status`, `output` |
| `sql_problems` | SQL challenge scenarios | `id`, `topic_id` (FK), `title`, `schema_sql`, `expected_query` |

---

## 3. Progress & Intelligence Domain

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `topic_progress` | User mastery per topic | `user_id` (FK), `topic_id` (FK), `status`, `theory_completion`, `practice_completion`, `assessment_completion`, `revision_completion`, `mastery_percent` |
| `practical_progress` | Lab experiment tracking | `user_id` (FK), `practical_id` (FK), `status`, `code_content`, `output_notes` |
| `mistakes` | Mistakes notebook entries | `user_id` (FK), `topic_id` (FK), `description`, `correction`, `is_resolved` |
| `revision_items` | Spaced repetition queue | `user_id` (FK), `topic_id` (FK), `next_revision_at`, `priority` |
| `study_sessions` | Time spent tracking | `user_id` (FK), `duration_minutes`, `activity_type` |
| `notes` | User markdown notes | `user_id` (FK), `topic_id` (FK), `content` |
| `bookmarks` | Bookmarked resources | `user_id` (FK), `topic_id` (FK), `note` |
| `daily_goals` | Daily streak targets | `user_id` (FK), `target_date`, `is_completed` |
| `achievements` | Badges and rewards | `user_id` (FK), `badge_type`, `awarded_at` |

---

## 4. User Domain

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | User credentials & roles | `id`, `username` (UNIQUE), `email` (UNIQUE), `hashed_password`, `is_admin` |
