// Core TypeScript type definitions for Semester OS frontend

export type TopicStatus = 'NOT_STARTED' | 'LEARNING' | 'LEARNED' | 'NEEDS_REVISION';
export type PracticalStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'NEEDS_REDO';
export type SourceType = 'OFFICIAL_SYLLABUS' | 'ADDITIONAL_LEARNING' | 'USER_CREATED';
export type Difficulty = 'EASY' | 'MEDIUM' | 'HARD';
export type QuestionType = 'MCQ' | 'MULTIPLE_ANSWER' | 'TRUE_FALSE' | 'FILL_BLANK' | 'SHORT_ANSWER' | 'OUTPUT_PREDICTION' | 'DEBUGGING' | 'CODING' | 'SQL';

// ── Auth ──────────────────────────────────────────────────────────────
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// ── Curriculum ────────────────────────────────────────────────────────
export interface Topic {
  id: number;
  unit_id: number;
  name: string;
  description: string | null;
  sort_order: number;
  source_type: SourceType;
  has_coding: boolean;
  has_practical: boolean;
}

export interface Unit {
  id: number;
  subject_id: number;
  unit_number: number;
  name: string;
  description: string | null;
  sort_order: number;
  topics: Topic[];
}

export interface Subject {
  id: number;
  course_code: string;
  name: string;
  credits: number;
  description: string | null;
  sort_order: number;
  units: Unit[];
}

export interface SubjectSummary {
  id: number;
  course_code: string;
  name: string;
  credits: number;
  description: string | null;
  sort_order: number;
}

export interface Practical {
  id: number;
  subject_id: number;
  unit_id: number | null;
  practical_number: number;
  title: string;
  objective: string | null;
  description: string | null;
  source_type: SourceType;
  sort_order: number;
}

export interface PracticalItem {
  id: number;
  subject_id: number;
  course_code: string;
  subject_name: string;
  practical_number: number;
  title: string;
  objective: string | null;
  description: string | null;
  status: PracticalStatus;
  code_content: string | null;
  output_notes: string | null;
  notes: string | null;
  completed_at: string | null;
}

// ── Progress ──────────────────────────────────────────────────────────
export interface TopicProgress {
  id: number;
  user_id: number;
  topic_id: number;
  status: TopicStatus;
  theory_completion: number;
  practice_completion: number;
  assessment_completion: number;
  revision_completion: number;
  mastery_percent: number;
  notes_read: boolean;
  practice_completed: boolean;
  quiz_completed: boolean;
  coding_completed: boolean;
  practical_completed: boolean;
  confidence_level: number;
  revision_count: number;
  quiz_best_score: number | null;
  quiz_attempt_count: number;
  last_studied_at: string | null;
  first_learned_at: string | null;
  last_revised_at: string | null;
  updated_at: string;
}

export interface TopicProgressUpdate {
  status?: TopicStatus;
  theory_completion?: number;
  practice_completion?: number;
  assessment_completion?: number;
  revision_completion?: number;
  notes_read?: boolean;
  practice_completed?: boolean;
  quiz_completed?: boolean;
  coding_completed?: boolean;
  practical_completed?: boolean;
  confidence_level?: number;
}

export interface PracticalProgress {
  id: number;
  user_id: number;
  practical_id: number;
  status: PracticalStatus;
  code_content: string | null;
  output_notes: string | null;
  notes: string | null;
  completed_at: string | null;
  updated_at: string;
}

export interface SubjectProgress {
  subject_id: number;
  course_code: string;
  subject_name: string;
  total_topics: number;
  learned_topics: number;
  learning_topics: number;
  needs_revision_topics: number;
  not_started_topics: number;
  completion_percent: number;
  average_mastery: number;
  total_practicals: number;
  completed_practicals: number;
  practical_completion_percent: number;
}

export interface Dashboard {
  overall_completion_percent: number;
  total_topics: number;
  learned_topics: number;
  needs_revision_topics: number;
  total_practicals: number;
  completed_practicals: number;
  subjects: SubjectProgress[];
  study_streak_days: number;
  total_study_minutes: number;
  today_study_minutes: number;
  recent_topics: RecentTopic[];
  weak_topics: WeakTopic[];
  revision_due_count: number;
  continue_studying?: ContinueStudyingTarget | null;
  recommended_action?: RecommendedAction | null;
}

export interface ContinueStudyingTarget {
  topic_id: number;
  topic_name: string;
  unit_number: number;
  course_code: string;
  subject_name: string;
  mastery_percent: number;
  last_studied_ago: string;
  next_action_label: string;
  to: string;
}

export interface RecommendedAction {
  title: string;
  subtitle: string;
  action_text: string;
  to: string;
}

export interface RecentTopic {
  topic_id: number;
  topic_name: string;
  unit_id: number;
  unit_number?: number;
  course_code?: string;
  subject_id?: number;
  status: TopicStatus;
  mastery_percent: number;
  last_studied_at: string | null;
}

export interface WeakTopic {
  topic_id: number;
  topic_name: string;
  unit_id?: number;
  unit_number?: number;
  course_code?: string;
  subject_name?: string;
  mastery_percent: number;
  reason: string;
  priority_score?: number;
  mistake_count?: number;
  to?: string;
}

export interface StudySession {
  id: number;
  user_id: number;
  topic_id?: number | null;
  session_type: string;
  duration_minutes: number;
  notes?: string | null;
  started_at: string;
  ended_at?: string | null;
}

export interface TopicWorkspace {
  topic: {
    id: number;
    name: string;
    description: string | null;
    has_coding: boolean;
  };
  unit: {
    id: number;
    unit_number: number;
    name: string;
  };
  subject: {
    id: number;
    course_code: string;
    name: string;
  };
  progress: TopicProgress;
  notes: Note[];
  questions_count: number;
  coding_problem?: {
    id: number;
    title: string;
    description: string;
    language: string;
    difficulty: Difficulty;
    starter_code: string | null;
    hints: string | null;
  } | null;
  next_topic?: { id: number; name: string } | null;
  prev_topic?: { id: number; name: string } | null;
}

export interface Note {
  id: number;
  topic_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CurriculumAudit {
  valid: boolean;
  subject_count: number;
  total_units: number;
  course_codes: string[];
  errors: string[];
  warnings: string[];
  subjects: {
    course_code: string;
    name: string;
    unit_count: number;
    topic_count: number;
  }[];
  stats?: Record<string, any>;
}

// ── Practice & Tests ───────────────────────────────────────────────────
export interface Option {
  id: number;
  option_text: string;
  is_correct?: boolean;
  sort_order: number;
}

export interface Question {
  id: number;
  topic_id: number;
  question_text: string;
  question_type: QuestionType;
  difficulty: Difficulty;
  explanation: string | null;
  source_type: string;
  options: Option[];
}

export interface PracticeAttemptResult {
  id: number;
  question_id: number;
  topic_id?: number;
  is_correct: boolean;
  score: number;
  explanation: string | null;
  correct_option_id: number | null;
  attempted_at: string;
}

export interface TestSession {
  session_id: string;
  scope: string;
  scope_title: string;
  time_limit_minutes: number;
  questions: Question[];
}

export interface TestResult {
  session_id: string;
  total_questions: number;
  correct_count: number;
  incorrect_count: number;
  skipped_count: number;
  score_percentage: number;
  passed: boolean;
  weak_topics: {
    topic_id: number;
    topic_name: string;
    course_code: string;
    unit_number: number;
  }[];
  recommended_revision: string[];
  details: {
    question_id: number;
    question_text: string;
    is_correct: boolean;
    selected_option_id?: number;
    correct_option_id?: number;
    correct_option_text?: string;
    explanation?: string;
    topic_name?: string;
  }[];
}

export interface Mistake {
  id: number;
  topic_id: number;
  topic_name: string | null;
  course_code: string | null;
  description: string;
  correction: string | null;
  source_type: string;
  is_resolved: boolean;
  created_at: string;
}

// ── Coding & SQL ───────────────────────────────────────────────────────
export interface LanguageInfo {
  id: string;
  display_name: string;
  category: string;
  file_name: string;
  entry_point: string;
  starter_code: string;
  supports_stdin: boolean;
  timeout_seconds: number;
  course_code: string;
  description: string;
}

export interface PublicTestCase {
  test_index: number;
  input_text: string;
  expected_output: string;
  actual_output?: string;
  passed?: boolean;
  status?: string;
}

export interface CodingProblem {
  id: number;
  topic_id: number;
  topic_name?: string;
  course_code?: string;
  unit_number?: number;
  title: string;
  description: string;
  language: string;
  difficulty: Difficulty;
  starter_code: string | null;
  expected_output: string | null;
  hints: string | null;
  examples: string | null;
  source_type: string;
  is_solved?: boolean;
  public_test_cases?: PublicTestCase[];
}

export interface CodeExecuteRequest {
  language: string;
  source_code: string;
  stdin?: string;
}

export interface CodeExecuteResult {
  status: string; // ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SYSTEM_ERROR
  stdout: string;
  stderr: string;
  compile_error?: string | null;
  runtime_error?: string | null;
  execution_time_ms: number;
  memory_usage_mb: number;
  exit_code: number;
}

export interface PracticeSubmitResult {
  id: number;
  problem_id: number;
  status: string;
  passed: boolean;
  tests_passed: number;
  tests_total: number;
  public_test_results: PublicTestCase[];
  hidden_passed: number;
  hidden_total: number;
  execution_time_ms: number;
  output_message: string;
  compile_error?: string | null;
  runtime_error?: string | null;
  submitted_at: string;
}

export interface CodingSubmissionResult {
  id: number;
  problem_id: number;
  code: string;
  language: string;
  status: string;
  output: string | null;
  passed: boolean;
  submitted_at: string;
}

export interface SqlExecutionResult {
  success: boolean;
  columns: string[];
  rows: string[][];
  error?: string | null;
  row_count: number;
}

// ── Revision & Intelligence ────────────────────────────────────────────
export interface RevisionQueueItem {
  topic_id: number;
  topic_name: string;
  course_code: string;
  unit_number: number;
  unit_name: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  mastery_percent: number;
  status: TopicStatus;
  reason: string;
  last_studied_at: string | null;
}

export interface StudyRecommendationBlock {
  duration_minutes: number;
  title: string;
  subject: string;
  unit: string;
  topic_id: number | null;
  type: 'REVISION' | 'NEW_THEORY' | 'CODING' | 'QUIZ';
  reason: string;
}

export interface StudyRecommendationPlan {
  session_title: string;
  total_minutes: number;
  blocks: StudyRecommendationBlock[];
  generated_at: string;
}

export interface DetailedAnalytics {
  subject_breakdown: {
    course_code: string;
    name: string;
    learned: number;
    learning: number;
    needs_revision: number;
    not_started: number;
    average_mastery: number;
    completion_pct: number;
  }[];
  total_attempts: number;
  correct_attempts: number;
  overall_accuracy_percent: number;
  study_streak_days: number;
}

export interface SearchResult {
  type: 'SUBJECT' | 'UNIT' | 'TOPIC' | 'PRACTICAL' | 'CODING';
  title: string;
  subtitle: string;
  url: string;
}

// ── Exam Preparation & Simulator ───────────────────────────────────────
export interface ExamBlueprint {
  exam_type: 'MIDTERM' | 'END_TERM';
  title: string;
  description: string;
  coverage_units: number[];
  mcq_count: number;
  descriptive_count: number;
  descriptive_marks_per_q: number;
  duration_minutes: number;
  total_marks: number;
  part_a_title: string;
  part_b_title: string;
}

export interface ExamReadinessUnit {
  unit_number: number;
  title: string;
  mastery_percent: number;
  topics_count: number;
  topics_mastered: number;
  mcq_accuracy: number;
}

export interface ExamReadinessSubject {
  subject_id: number;
  course_code: string;
  subject_name: string;
  midterm_readiness_percent: number;
  endterm_readiness_percent: number;
  units: ExamReadinessUnit[];
  weak_topics: string[];
}

export interface ExamReadiness {
  overall_midterm_readiness: number;
  overall_endterm_readiness: number;
  upcoming_exam: 'MIDTERM' | 'END_TERM';
  days_remaining: number | null;
  target_date: string | null;
  subjects: ExamReadinessSubject[];
  weakest_subject: string | null;
  weakest_unit_info: string | null;
}

export interface DescriptiveQuestion {
  id: number;
  subject_id: number;
  course_code?: string | null;
  unit_id: number;
  unit_number?: number | null;
  topic_id: number;
  topic_name?: string | null;
  question_text: string;
  marks: number;
  difficulty: Difficulty;
  question_type: string;
  answer_outline: string[];
  model_answer: string;
  key_points: string[];
  exam_tips: string[];
  important_terms: string[];
  diagram_guidance?: string | null;
  code_guidance?: string | null;
  is_solved: boolean;
  latest_score?: number | null;
}

export interface DescriptiveSubmissionResult {
  id: number;
  question_id: number;
  self_score: number;
  status: string;
  checklist_completed: string[];
  submitted_at: string;
}

export interface ExamMCQOption {
  id: number;
  option_text: string;
  sort_order: number;
}

export interface ExamMCQQuestion {
  id: number;
  topic_id: number;
  topic_name?: string | null;
  unit_number?: number | null;
  course_code?: string | null;
  question_text: string;
  difficulty: Difficulty;
  options: ExamMCQOption[];
}

export interface ExamSession {
  session_id: string;
  exam_type: 'MIDTERM' | 'END_TERM';
  subject_id?: number | null;
  subject_name?: string | null;
  course_code?: string | null;
  duration_minutes: number;
  total_marks: number;
  mcqs: ExamMCQQuestion[];
  descriptive_questions: DescriptiveQuestion[];
  created_at: string;
  expires_at: string;
}

export interface UnitScoreBreakdown {
  unit_number: number;
  questions_count: number;
  correct_count: number;
  accuracy_percent: number;
}

export interface ExamReviewQuestion {
  question_id: number;
  question_text: string;
  topic_name?: string | null;
  unit_number?: number | null;
  user_selected_option_id?: number | null;
  user_selected_option_text?: string | null;
  correct_option_id: number;
  correct_option_text: string;
  is_correct: boolean;
  explanation?: string | null;
}

export interface ExamResult {
  session_id: string;
  exam_type: 'MIDTERM' | 'END_TERM';
  score: number;
  total_marks: number;
  percentage: number;
  mcqs_total: number;
  mcqs_correct: number;
  mcqs_incorrect: number;
  mcqs_unanswered: number;
  accuracy_percent: number;
  descriptive_total: number;
  descriptive_attempted: number;
  unit_breakdown: UnitScoreBreakdown[];
  weak_topics: string[];
  mistakes_logged_count: number;
  review_mcqs: ExamReviewQuestion[];
  submitted_at: string;
}
