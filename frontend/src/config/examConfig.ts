export interface ClientExamConfig {
  examType: 'MIDTERM' | 'END_TERM';
  title: string;
  badge: string;
  description: string;
  coverageUnits: number[];
  mcqCount: number;
  descriptiveCount: number;
  descriptiveMarksPerQ: number;
  durationMinutes: number;
  totalMarks: number;
  partATitle: string;
  partBTitle: string;
}

export const CLIENT_EXAM_CONFIGS: Record<'MIDTERM' | 'END_TERM', ClientExamConfig> = {
  MIDTERM: {
    examType: 'MIDTERM',
    title: 'University Midterm Examination',
    badge: '30 MCQs · Units 1–3 · 60 Mins',
    description: 'Covers the first 3 chapters/units across the semester syllabus with exactly 30 timed multiple-choice questions.',
    coverageUnits: [1, 2, 3],
    mcqCount: 30,
    descriptiveCount: 0,
    descriptiveMarksPerQ: 0,
    durationMinutes: 60,
    totalMarks: 30,
    partATitle: 'Section 1: Objective MCQs (30 Questions · 30 Marks)',
    partBTitle: '',
  },
  END_TERM: {
    examType: 'END_TERM',
    title: 'University End-Term Examination',
    badge: '30 MCQs + 5 Descriptive · Full Syllabus · 120 Mins',
    description: 'Comprehensive examination covering the entire 6-unit syllabus with Part A (30 MCQs) and Part B (5 × 10-Mark Descriptive Questions).',
    coverageUnits: [1, 2, 3, 4, 5, 6],
    mcqCount: 30,
    descriptiveCount: 5,
    descriptiveMarksPerQ: 10,
    durationMinutes: 120,
    totalMarks: 80,
    partATitle: 'Part A: Objective MCQs (30 Questions · 30 Marks)',
    partBTitle: 'Part B: Descriptive / Analytical Questions (5 Questions · 50 Marks)',
  },
};
