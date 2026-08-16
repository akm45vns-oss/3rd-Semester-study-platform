import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Play } from 'lucide-react';
import { examsApi, curriculumApi } from '../api';
import type { DescriptiveQuestion, SubjectSummary } from '../types';
import { CLIENT_EXAM_CONFIGS } from '../config/examConfig';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function ExamsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [activeExamType, setActiveExamType] = useState<'MIDTERM' | 'END_TERM'>('MIDTERM');
  const [descriptiveQuestions, setDescriptiveQuestions] = useState<DescriptiveQuestion[]>([]);

  useEffect(() => {
    curriculumApi.getSubjects().then(subs => {
      setSubjects(subs);
      const subParam = searchParams.get('subject_id');
      if (subParam) {
        setSelectedSubjectId(Number(subParam));
      }
    });

    examsApi.getDescriptiveQuestions().then(setDescriptiveQuestions).catch(console.error);
  }, [searchParams]);

  const activeSubject = subjects.find(s => s.id === selectedSubjectId) || null;
  const config = CLIENT_EXAM_CONFIGS[activeExamType];

  const handleSelectSubject = (id: number | null) => {
    setSelectedSubjectId(id);
    if (id) {
      setSearchParams({ subject_id: id.toString() });
    } else {
      setSearchParams({});
    }
  };

  const handleStartMock = () => {
    let url = `/exams/mock?type=${activeExamType}`;
    if (selectedSubjectId) {
      url += `&subject_id=${selectedSubjectId}`;
    }
    navigate(url);
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        <Breadcrumb items={[{ label: 'Home', to: '/dashboard' }, { label: 'Exam Center' }]} />

        {/* ── Top Header ── */}
        <div className="pb-2 border-b border-slate-200">
          <h1 className="text-xl sm:text-2xl font-bold font-heading text-slate-900">
            Exam Center &amp; Mock Simulations
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Full-length timed examinations calibrated to university blueprints
          </p>
        </div>

        {/* ── Choose Subject Scope ── */}
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            1. Select Subject Scope
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
            <button
              onClick={() => handleSelectSubject(null)}
              className={`p-2.5 rounded-lg border text-center text-xs font-semibold transition-all ${
                selectedSubjectId === null
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-700'
              }`}
            >
              All Subjects
            </button>
            {subjects.map(s => (
              <button
                key={s.id}
                onClick={() => handleSelectSubject(s.id)}
                className={`p-2.5 rounded-lg border text-center text-xs transition-all ${
                  selectedSubjectId === s.id
                    ? 'bg-slate-900 text-white border-slate-900 shadow-sm font-semibold'
                    : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                <div className="font-mono font-bold text-[11px]">{s.course_code}</div>
                <div className="text-[10px] truncate opacity-75">{s.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Choose Exam Type ── */}
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            2. Choose Examination Format
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              onClick={() => setActiveExamType('MIDTERM')}
              className={`p-5 rounded-xl border text-left space-y-2 transition-all ${
                activeExamType === 'MIDTERM'
                  ? 'bg-white border-slate-900 shadow-md ring-1 ring-slate-900'
                  : 'bg-white hover:border-slate-300 border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="badge-brand font-mono font-bold text-[10px]">60 Minutes</span>
                <span className="text-xs font-bold text-slate-900">30 Marks</span>
              </div>
              <h3 className="text-base font-bold text-slate-900">Midterm Examination</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                30 MCQs covering Units 1, 2, and 3. Timed simulation with instantaneous score calculation.
              </p>
            </button>

            <button
              onClick={() => setActiveExamType('END_TERM')}
              className={`p-5 rounded-xl border text-left space-y-2 transition-all ${
                activeExamType === 'END_TERM'
                  ? 'bg-white border-slate-900 shadow-md ring-1 ring-slate-900'
                  : 'bg-white hover:border-slate-300 border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="badge-brand font-mono font-bold text-[10px]">120 Minutes</span>
                <span className="text-xs font-bold text-slate-900">80 Marks</span>
              </div>
              <h3 className="text-base font-bold text-slate-900">End-Term Examination</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Comprehensive 30 MCQs (30 marks) + 5 Analytical Descriptive Questions (50 marks) covering all 6 units.
              </p>
            </button>
          </div>
        </div>

        {/* ── Start Mock Action Bar ── */}
        <div className="card p-5 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-0.5">
            <div className="text-sm font-bold text-slate-900">
              Ready to begin {activeExamType === 'MIDTERM' ? 'Midterm Mock' : 'End-Term Mock'}?
            </div>
            <div className="text-xs text-slate-500">
              Scope: {activeSubject ? `${activeSubject.name} (${activeSubject.course_code})` : 'All Semester Subjects'} · {config.durationMinutes} minutes
            </div>
          </div>

          <button
            onClick={handleStartMock}
            className="btn-primary text-xs py-2.5 px-6 flex items-center gap-2 shrink-0 justify-center shadow-sm"
          >
            <Play size={13} className="fill-white" />
            <span>Launch Mock Exam</span>
          </button>
        </div>

        {/* ── 10-Mark Descriptive Questions Bank Preview ── */}
        {descriptiveQuestions.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                10-Mark Descriptive Question Bank ({descriptiveQuestions.length})
              </div>
            </div>

            <div className="space-y-2">
              {descriptiveQuestions.slice(0, 5).map(q => (
                <div key={q.id} className="card p-4 hover:border-slate-300 transition-all flex items-center justify-between gap-3">
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {q.course_code && <span className="badge-brand font-mono font-bold text-[10px]">{q.course_code}</span>}
                      <span className="text-xs font-semibold text-slate-700 truncate">{q.topic_name}</span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{q.question_text}</h4>
                  </div>
                  <span className="badge-brand font-mono text-[10px] font-bold shrink-0">10 Marks</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
