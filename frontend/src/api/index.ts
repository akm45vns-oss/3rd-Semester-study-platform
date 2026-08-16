import apiClient from './client';
import { withCache, clientCache } from './cache';
import type {
  User, Token, Subject, SubjectSummary, Unit, Topic,
  Practical, PracticalItem, TopicProgress, TopicProgressUpdate,
  PracticalProgress, SubjectProgress, Dashboard,
  Note, CurriculumAudit, Question, PracticeAttemptResult,
  TestSession, TestResult, Mistake, CodingProblem,
  SqlExecutionResult, RevisionQueueItem,
  StudyRecommendationPlan, DetailedAnalytics, SearchResult,
  Difficulty, StudySession, TopicWorkspace,
  LanguageInfo, CodeExecuteRequest, CodeExecuteResult, PracticeSubmitResult,
} from '../types';

// ── Auth ──────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { username: string; email: string; password: string; full_name?: string }) =>
    apiClient.post<User>('/auth/register', data).then(r => r.data),

  login: (username: string, password: string) =>
    apiClient.post<Token>('/auth/login', { username, password }).then(r => r.data),

  me: () =>
    apiClient.get<User>('/auth/me').then(r => r.data),
};

// ── Curriculum (Cached) ────────────────────────────────────────────────
export const curriculumApi = {
  getSubjects: () =>
    withCache('subjects_all', () => apiClient.get<SubjectSummary[]>('/subjects').then(r => r.data), 600),

  getSubject: (id: number) =>
    withCache(`subject_${id}`, () => apiClient.get<Subject>(`/subjects/${id}`).then(r => r.data), 600),

  getSubjectUnits: (subjectId: number) =>
    withCache(`subject_units_${subjectId}`, () => apiClient.get<Unit[]>(`/subjects/${subjectId}/units`).then(r => r.data), 600),

  getSubjectPracticals: (subjectId: number) =>
    withCache(`subject_practicals_${subjectId}`, () => apiClient.get<Practical[]>(`/subjects/${subjectId}/practicals`).then(r => r.data), 600),

  getUnit: (id: number) =>
    withCache(`unit_${id}`, () => apiClient.get<Unit>(`/units/${id}`).then(r => r.data), 600),

  getTopic: (id: number) =>
    withCache(`topic_${id}`, () => apiClient.get<Topic>(`/topics/${id}`).then(r => r.data), 600),

  auditCurriculum: () =>
    withCache('curriculum_audit', () => apiClient.get<CurriculumAudit>('/curriculum/audit').then(r => r.data), 900),

  prefetchSubject: (id: number) => {
    curriculumApi.getSubject(id);
    curriculumApi.getSubjectUnits(id);
    curriculumApi.getSubjectPracticals(id);
  },
};

// ── Progress & Workspace ───────────────────────────────────────────────
export const progressApi = {
  getTopicProgress: (topicId: number) =>
    apiClient.get<TopicProgress>(`/progress/topics/${topicId}`).then(r => r.data),

  updateTopicProgress: (topicId: number, data: TopicProgressUpdate) => {
    clientCache.invalidate('topic_');
    return apiClient.post<TopicProgress>(`/progress/topics/${topicId}`, data).then(r => r.data);
  },

  getTopicWorkspace: (topicId: number) =>
    apiClient.get<TopicWorkspace>(`/topics/${topicId}/workspace`).then(r => r.data),

  getPracticalProgress: (practicalId: number) =>
    apiClient.get<PracticalProgress>(`/progress/practicals/${practicalId}`).then(r => r.data),

  updatePracticalProgress: (practicalId: number, data: Partial<PracticalProgress>) => {
    clientCache.invalidate('practical_');
    return apiClient.post<PracticalProgress>(`/progress/practicals/${practicalId}`, data).then(r => r.data);
  },

  getSubjectProgress: (subjectId: number) =>
    apiClient.get<SubjectProgress>(`/progress/subjects/${subjectId}`).then(r => r.data),

  getDashboard: () =>
    apiClient.get<Dashboard>('/dashboard').then(r => r.data),

  getTopicNotes: (topicId: number) =>
    withCache(`topic_notes_${topicId}`, () => apiClient.get<Note[]>(`/topics/${topicId}/notes`).then(r => r.data), 300),

  createTopicNote: (topicId: number, content: string) => {
    clientCache.invalidate(`topic_notes_${topicId}`);
    return apiClient.post<Note>(`/topics/${topicId}/notes`, { content }).then(r => r.data);
  },

  startStudySession: (data: { topic_id?: number; session_type?: string }) =>
    apiClient.post<StudySession>('/progress/study-sessions/start', data).then(r => r.data),

  finishStudySession: (sessionId: number, data: { notes?: string; topics_studied?: number; mcqs_attempted?: number }) =>
    apiClient.post<StudySession>(`/progress/study-sessions/${sessionId}/finish`, data).then(r => r.data),

  getActiveStudySession: () =>
    apiClient.get<StudySession | null>('/progress/study-sessions/active').then(r => r.data),
};

// ── Practice & Tests ───────────────────────────────────────────────────
export const practiceApi = {
  getQuestions: (params?: { topic_id?: number; unit_id?: number; subject_id?: number; difficulty?: Difficulty; limit?: number }) =>
    apiClient.get<Question[]>('/practice/questions', { params }).then(r => r.data),

  submitAttempt: (data: { question_id: number; selected_option_id?: number; answer_text?: string; time_taken_seconds?: number; session_id?: string }) => {
    clientCache.invalidate('topic_');
    return apiClient.post<PracticeAttemptResult>('/practice/attempts', data).then(r => r.data);
  },

  generateTest: (data: { scope: 'TOPIC' | 'UNIT' | 'SUBJECT' | 'FULL_MOCK'; topic_id?: number; unit_id?: number; subject_id?: number; question_count?: number; difficulty?: Difficulty }) =>
    apiClient.post<TestSession>('/practice/tests/generate', data).then(r => r.data),

  submitTest: (data: { session_id: string; scope: string; answers: { question_id: number; selected_option_id?: number; answer_text?: string; time_taken_seconds?: number }[] }) => {
    clientCache.invalidate('topic_');
    return apiClient.post<TestResult>('/practice/tests/submit', data).then(r => r.data);
  },

  getMistakes: (is_resolved?: boolean) =>
    apiClient.get<Mistake[]>('/practice/mistakes', { params: { is_resolved } }).then(r => r.data),

  resolveMistake: (id: number) =>
    apiClient.post<{ status: string }>(`/practice/mistakes/${id}/resolve`).then(r => r.data),
};

// ── Coding Lab & Online Compiler ──────────────────────────────────────
export const codingApi = {
  getLanguages: () =>
    withCache('coding_languages', () => apiClient.get<LanguageInfo[]>('/coding/languages').then(r => r.data), 3600),

  getProblems: (params?: { language?: string; difficulty?: Difficulty; subject_id?: number; unit_id?: number; topic_id?: number; solved?: boolean }) =>
    withCache(`coding_problems_${params?.language || 'all'}_${params?.difficulty || 'all'}_${params?.subject_id || 'all'}_${params?.unit_id || 'all'}_${params?.topic_id || 'all'}_${params?.solved ?? 'all'}`, () =>
      apiClient.get<CodingProblem[]>('/coding/problems', { params }).then(r => r.data), 180),

  getRecommendedProblems: () =>
    apiClient.get<CodingProblem[]>('/coding/problems/recommended').then(r => r.data),

  getProblem: (id: number) =>
    withCache(`coding_problem_${id}`, () => apiClient.get<CodingProblem>(`/coding/problems/${id}`).then(r => r.data), 600),

  executeCode: (data: CodeExecuteRequest) =>
    apiClient.post<CodeExecuteResult>('/coding/execute', data).then(r => r.data),

  submitCode: (data: { problem_id: number; code: string; language: string }) => {
    clientCache.invalidate('coding_');
    clientCache.invalidate('dashboard_');
    clientCache.invalidate('topic_');
    return apiClient.post<PracticeSubmitResult>('/coding/submit', data).then(r => r.data);
  },

  executeSql: (query: string, schema_sql?: string) =>
    apiClient.post<SqlExecutionResult>('/coding/execute-sql', { query, schema_sql }).then(r => r.data),
};

// ── Intelligence & Revision ────────────────────────────────────────────
export const intelligenceApi = {
  getRevisionQueue: () =>
    apiClient.get<RevisionQueueItem[]>('/revision/queue').then(r => r.data),

  completeRevision: (topicId: number) => {
    clientCache.invalidate('topic_');
    return apiClient.post<{ status: string; mastery_percent: number }>(`/revision/${topicId}/complete`).then(r => r.data);
  },

  getWhatToStudyNow: () =>
    apiClient.get<StudyRecommendationPlan>('/recommendations/what-to-study').then(r => r.data),

  getAllPracticals: (subject_id?: number) =>
    withCache(`all_practicals_${subject_id || 'all'}`, () =>
      apiClient.get<PracticalItem[]>('/practicals', { params: { subject_id } }).then(r => r.data), 600),

  getDetailedAnalytics: () =>
    apiClient.get<DetailedAnalytics>('/analytics/detailed').then(r => r.data),

  globalSearch: (q: string) =>
    apiClient.get<SearchResult[]>('/search', { params: { q } }).then(r => r.data),
};

// ── AI Study Assistant ──────────────────────────────────────────────────
export const aiApi = {
  getStatus: () =>
    apiClient.get<{ is_configured: boolean; provider: string; model: string }>('/ai/status').then(r => r.data),

  configureKey: (apiKey: string) =>
    apiClient.post<{ success: boolean; message: string }>('/ai/configure-key', { api_key: apiKey }).then(r => r.data),

  generateNotes: (topicId: number) => {
    clientCache.invalidate(`topic_notes_${topicId}`);
    return apiClient.post<{ success: boolean; topic_id: number; content: string }>(`/ai/generate-notes/${topicId}`).then(r => r.data);
  },

  generateQuiz: (topicId: number) =>
    apiClient.post<{ success: boolean; topic_id: number; questions_count: number }>(`/ai/generate-quiz/${topicId}`).then(r => r.data),
};

// ── Master Exam Preparation & Simulator ─────────────────────────────────
export const examsApi = {
  getBlueprints: () =>
    withCache('exam_blueprints', () =>
      apiClient.get<import('../types').ExamBlueprint[]>('/exams/blueprint').then(r => r.data), 1800),

  getReadiness: (subject_id?: number) =>
    apiClient.get<import('../types').ExamReadiness>('/exams/readiness', { params: { subject_id } }).then(r => r.data),

  generateMidtermMock: (subject_id?: number) =>
    apiClient.post<import('../types').ExamSession>('/exams/midterm/generate', null, { params: { subject_id } }).then(r => r.data),

  generateEndTermMock: (subject_id?: number) =>
    apiClient.post<import('../types').ExamSession>('/exams/endterm/generate', null, { params: { subject_id } }).then(r => r.data),

  submitExam: (data: {
    session_id: string;
    exam_type: string;
    subject_id?: number | null;
    time_taken_seconds: number;
    mcq_answers: { question_id: number; selected_option_id: number | null; marked_for_review: boolean }[];
    descriptive_answers?: { question_id: number; user_answer: string; self_score?: number | null; marked_for_review: boolean }[];
  }) => apiClient.post<import('../types').ExamResult>('/exams/submit', data).then(r => r.data),

  getDescriptiveQuestions: (params?: { subject_id?: number; unit_id?: number; difficulty?: string }) =>
    apiClient.get<import('../types').DescriptiveQuestion[]>('/exams/descriptive', { params }).then(r => r.data),

  submitDescriptiveAnswer: (data: {
    question_id: number;
    user_answer: string;
    self_score: number;
    checklist_completed: string[];
    status: string;
  }) => apiClient.post<import('../types').DescriptiveSubmissionResult>('/exams/descriptive/submit', data).then(r => r.data),
};

