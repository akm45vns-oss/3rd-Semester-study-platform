import { useEffect, useState, useCallback, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Clock, Flag, ChevronLeft, ChevronRight, Award,
  CheckCircle2, Grid, X, AlertCircle, RotateCcw,
} from 'lucide-react';
import { examsApi } from '../api';
import { extractErrorMessage } from '../api/client';
import type { ExamSession, ExamResult } from '../types';
import { AppLayout, Breadcrumb } from '../components/layout';
import { Spinner } from '../components/ui';
import { useAuthStore } from '../stores/authStore';

export default function ExamMockPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const examType = (searchParams.get('type') || 'MIDTERM').toUpperCase() as 'MIDTERM' | 'END_TERM';
  const subjectId = searchParams.get('subject_id') ? Number(searchParams.get('subject_id')) : undefined;

  const [session, setSession] = useState<ExamSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<'MCQ' | 'DESCRIPTIVE'>('MCQ');
  const [mobilePaletteOpen, setMobilePaletteOpen] = useState(false);

  // Answers & State
  const [mcqAnswers, setMcqAnswers] = useState<Record<number, number | null>>({});
  const [mcqReviews, setMcqReviews] = useState<Record<number, boolean>>({});
  const [descAnswers, setDescAnswers] = useState<Record<number, string>>({});
  const [descScores] = useState<Record<number, number>>({});

  // Timer & Submission
  const [secondsRemaining, setSecondsRemaining] = useState<number>(examType === 'MIDTERM' ? 3600 : 7200);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false);
  const [examResult, setExamResult] = useState<ExamResult | null>(null);

  const storageKey = `semester_os_exam_draft:${user?.id || 'guest'}:${examType}:${subjectId || 'all'}`;
  const isMountedRef = useRef(true);

  // 1. Initialize or Recover Existing Exam Session
  useEffect(() => {
    isMountedRef.current = true;
    setIsLoading(true);

    const savedDraft = localStorage.getItem(storageKey);
    if (savedDraft) {
      try {
        const parsed = JSON.parse(savedDraft);
        if (parsed.session && parsed.secondsRemaining > 0 && !parsed.isCompleted) {
          setSession(parsed.session);
          setMcqAnswers(parsed.mcqAnswers || {});
          setMcqReviews(parsed.mcqReviews || {});
          setDescAnswers(parsed.descAnswers || {});
          setSecondsRemaining(parsed.secondsRemaining);
          setIsLoading(false);
          return;
        }
      } catch {
        localStorage.removeItem(storageKey);
      }
    }

    const fetchSession = examType === 'MIDTERM'
      ? examsApi.generateMidtermMock(subjectId)
      : examsApi.generateEndTermMock(subjectId);

    fetchSession
      .then(res => {
        if (!isMountedRef.current) return;
        setSession(res);
        const durationSecs = res.duration_minutes * 60;
        setSecondsRemaining(durationSecs);
        localStorage.setItem(storageKey, JSON.stringify({
          session: res,
          mcqAnswers: {},
          mcqReviews: {},
          descAnswers: {},
          secondsRemaining: durationSecs,
          isCompleted: false,
          savedAt: Date.now(),
        }));
      })
      .catch(err => {
        console.error(err);
        alert(extractErrorMessage(err, 'Failed to generate mock examination.'));
        navigate('/exams');
      })
      .finally(() => {
        if (isMountedRef.current) setIsLoading(false);
      });

    return () => {
      isMountedRef.current = false;
    };
  }, [examType, subjectId, navigate, storageKey]);

  // 2. Persist answer changes locally per update
  useEffect(() => {
    if (!session || examResult) return;
    try {
      localStorage.setItem(storageKey, JSON.stringify({
        session,
        mcqAnswers,
        mcqReviews,
        descAnswers,
        secondsRemaining,
        isCompleted: false,
        savedAt: Date.now(),
      }));
    } catch {}
  }, [session, mcqAnswers, mcqReviews, descAnswers, secondsRemaining, examResult, storageKey]);

  // 3. Beforeunload navigation guard
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (session && !examResult) {
        e.preventDefault();
        e.returnValue = 'You have an active mock examination in progress. Your answers are saved.';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [session, examResult]);

  // 4. Timer countdown hook
  useEffect(() => {
    if (!session || examResult || isSubmitting) return;
    const interval = setInterval(() => {
      setSecondsRemaining(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          handleFinalSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [session, examResult, isSubmitting]);

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSelectMCQ = (qId: number, optId: number) => {
    setMcqAnswers(prev => ({ ...prev, [qId]: optId }));
  };

  const handleToggleReview = (qId: number) => {
    setMcqReviews(prev => ({ ...prev, [qId]: !prev[qId] }));
  };

  // 5. Safe Submission Handler
  const handleFinalSubmit = useCallback(async () => {
    if (!session || isSubmitting) return;
    setIsSubmitting(true);
    setSubmitError(null);
    setShowConfirmSubmit(false);

    try {
      const mcqSubmissions = session.mcqs.map(q => ({
        question_id: q.id,
        selected_option_id: mcqAnswers[q.id] || null,
        marked_for_review: !!mcqReviews[q.id],
      }));

      const descSubmissions = session.descriptive_questions.map(dq => ({
        question_id: dq.id,
        user_answer: descAnswers[dq.id] || '',
        self_score: descScores[dq.id] || 0,
        marked_for_review: false,
      }));

      const timeTaken = (session.duration_minutes * 60) - secondsRemaining;

      const res = await examsApi.submitExam({
        session_id: session.session_id,
        exam_type: session.exam_type,
        time_taken_seconds: Math.max(1, timeTaken),
        mcq_answers: mcqSubmissions,
        descriptive_answers: descSubmissions,
      });

      localStorage.removeItem(storageKey);
      setExamResult(res);
    } catch (err) {
      console.error('Exam submission failure:', err);
      setSubmitError(
        extractErrorMessage(err, 'Connection lost during submission. Your answers remain safely stored on this device.')
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [session, isSubmitting, mcqAnswers, mcqReviews, descAnswers, descScores, secondsRemaining, storageKey]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
          <Spinner size="lg" />
          <p className="text-xs font-semibold text-slate-500">
            Preparing examination session…
          </p>
        </div>
      </AppLayout>
    );
  }

  if (!session) {
    return (
      <AppLayout>
        <div className="p-8 text-center text-xs text-slate-500">
          Exam session not available.
        </div>
      </AppLayout>
    );
  }

  const totalMcqs = session.mcqs.length;
  const answeredMcqsCount = Object.values(mcqAnswers).filter(Boolean).length;
  const unansweredMcqsCount = totalMcqs - answeredMcqsCount;
  const markedReviewCount = Object.values(mcqReviews).filter(Boolean).length;

  // ── RESULT REVIEW VIEW ──
  if (examResult) {
    return (
      <AppLayout>
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
          <Breadcrumb items={[
            { label: 'Exams', to: '/exams' },
            { label: 'Result Summary' }
          ]} />

          {/* Top Score Banner */}
          <div className="card p-8 text-center space-y-4">
            <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mx-auto shadow-sm">
              <Award size={24} />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold font-heading text-slate-900">
              {session.exam_type === 'MIDTERM' ? 'Midterm Examination' : 'End-Term Examination'} Summary
            </h1>

            <div className="flex items-center justify-center gap-8 pt-2">
              <div>
                <div className="text-3xl font-bold font-mono text-slate-900">
                  {examResult.score.toFixed(1)} / {examResult.total_marks}
                </div>
                <div className="text-xs font-medium text-slate-500 mt-0.5">Total Marks</div>
              </div>
              <div className="h-10 w-px bg-slate-200" />
              <div>
                <div className="text-3xl font-bold font-mono text-blue-600">
                  {examResult.percentage.toFixed(0)}%
                </div>
                <div className="text-xs font-medium text-slate-500 mt-0.5">Percentage Grade</div>
              </div>
            </div>

            <div className="pt-3 flex gap-2 justify-center">
              <button onClick={() => navigate('/exams')} className="btn-primary text-xs">
                Back to Exam Center
              </button>
              <button onClick={() => navigate('/dashboard')} className="btn-secondary text-xs">
                Go to Dashboard
              </button>
            </div>
          </div>

          {/* Question-by-Question Review */}
          <div className="space-y-3">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Detailed Question Review</h2>

            {examResult.review_mcqs.map((q, idx) => {
              const isCorrect = q.is_correct;
              return (
                <div key={q.question_id} className="card p-5 space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-500">QUESTION {idx + 1}</span>
                    <span className={isCorrect ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                      {isCorrect ? '✓ Correct (+1 Mark)' : '✗ Incorrect (0 Marks)'}
                    </span>
                  </div>

                  <div className="text-sm font-bold text-slate-900">
                    {q.question_text}
                  </div>

                  <div className="space-y-2 pt-1 text-xs">
                    <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 font-semibold flex items-center justify-between">
                      <span><strong>Correct Answer: </strong>{q.correct_option_text}</span>
                      <CheckCircle2 size={15} className="text-emerald-600" />
                    </div>

                    {!isCorrect && (
                      <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 font-medium">
                        <span><strong>Your Selection: </strong>{q.user_selected_option_text || 'No option selected (Skipped)'}</span>
                      </div>
                    )}
                  </div>

                  {q.explanation && (
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700 leading-relaxed">
                      <strong>Explanation: </strong>{q.explanation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </AppLayout>
    );
  }

  const currentMcq = session.mcqs[currentIndex];
  const currentDesc = session.descriptive_questions[currentIndex];

  // ── ACTIVE EXAM SIMULATOR VIEW ──
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-blue-100 selection:text-blue-900">
      {/* ── Minimalist Exam Header ── */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="font-bold text-sm text-slate-900 tracking-tight font-heading">STUDYFORGE</span>
          <span className="badge-brand font-mono text-[10px] font-bold">
            {session.exam_type === 'MIDTERM' ? 'Midterm Mock (30 MCQs)' : 'End-Term Mock (80 Marks)'}
          </span>
        </div>

        <div className="flex items-center gap-3 font-mono font-bold text-xs">
          <div className="flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200 text-slate-900">
            <Clock size={13} className="text-slate-600" />
            <span>{formatTimer(secondsRemaining)}</span>
          </div>

          <button
            onClick={() => setMobilePaletteOpen(true)}
            className="md:hidden p-1.5 bg-slate-100 rounded text-slate-700 border border-slate-200"
            title="Open question palette"
          >
            <Grid size={14} />
          </button>
        </div>
      </header>

      {/* Network Failure Banner */}
      {submitError && (
        <div className="max-w-6xl w-full mx-auto px-4 pt-4">
          <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm animate-fade-in">
            <div className="flex items-start gap-2.5">
              <AlertCircle size={18} className="text-amber-700 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-bold text-amber-900">Submission Network Notice</div>
                <div className="text-xs text-amber-800">{submitError}</div>
              </div>
            </div>
            <button
              onClick={handleFinalSubmit}
              disabled={isSubmitting}
              className="btn-primary text-xs py-1.5 px-4 shrink-0 flex items-center gap-1.5"
            >
              <RotateCcw size={13} />
              <span>Retry Submission</span>
            </button>
          </div>
        </div>
      )}

      {/* ── Main Exam Container ── */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 md:grid-cols-12 gap-5 items-start">
        {/* Left Column: Question Card & Controls (Col 8) */}
        <div className="md:col-span-8 space-y-4">
          {session.exam_type === 'END_TERM' && (
            <div className="flex gap-2 bg-slate-100 p-1 rounded-lg border border-slate-200">
              <button
                onClick={() => { setActiveTab('MCQ'); setCurrentIndex(0); }}
                className={`flex-1 py-1.5 rounded text-xs font-semibold transition-all ${
                  activeTab === 'MCQ' ? 'bg-slate-900 text-white' : 'text-slate-600'
                }`}
              >
                Part A: 30 MCQs (30 Marks)
              </button>
              <button
                onClick={() => { setActiveTab('DESCRIPTIVE'); setCurrentIndex(0); }}
                className={`flex-1 py-1.5 rounded text-xs font-semibold transition-all ${
                  activeTab === 'DESCRIPTIVE' ? 'bg-slate-900 text-white' : 'text-slate-600'
                }`}
              >
                Part B: 5 Descriptive (50 Marks)
              </button>
            </div>
          )}

          {/* Question Box */}
          {activeTab === 'MCQ' && currentMcq && (
            <div className="card p-6 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="font-mono text-xs font-semibold text-slate-500">
                  Question {currentIndex + 1} of {session.mcqs.length}
                </span>

                <button
                  onClick={() => handleToggleReview(currentMcq.id)}
                  className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded border transition-colors ${
                    mcqReviews[currentMcq.id]
                      ? 'bg-amber-50 text-amber-900 border-amber-300'
                      : 'bg-slate-50 text-slate-600 border-slate-200'
                  }`}
                >
                  <Flag size={12} />
                  <span>{mcqReviews[currentMcq.id] ? 'Marked for Review' : 'Mark for Review'}</span>
                </button>
              </div>

              <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                {currentMcq.question_text}
              </h2>

              <div className="space-y-2.5 pt-1">
                {currentMcq.options.map((opt, idx) => {
                  const isSelected = mcqAnswers[currentMcq.id] === opt.id;
                  return (
                    <button
                      key={opt.id}
                      onClick={() => handleSelectMCQ(currentMcq.id, opt.id)}
                      className={`w-full p-3.5 rounded-lg border text-left text-xs font-semibold flex items-center justify-between transition-all ${
                        isSelected
                          ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-800 border-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className={`w-5 h-5 rounded flex items-center justify-center font-mono font-bold text-[10px] ${
                          isSelected ? 'bg-white text-slate-900' : 'bg-white border border-slate-200 text-slate-700'
                        }`}>
                          {String.fromCharCode(65 + idx)}
                        </span>
                        <span>{opt.option_text}</span>
                      </div>
                      {isSelected && <CheckCircle2 size={16} className="text-white" />}
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                <button
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex(i => i - 1)}
                  className="btn-secondary text-xs flex items-center gap-1"
                >
                  <ChevronLeft size={13} />
                  <span>Previous</span>
                </button>

                {currentIndex < session.mcqs.length - 1 ? (
                  <button
                    onClick={() => setCurrentIndex(i => i + 1)}
                    className="btn-primary text-xs flex items-center gap-1"
                  >
                    <span>Next</span>
                    <ChevronRight size={13} />
                  </button>
                ) : (
                  <button
                    onClick={() => setShowConfirmSubmit(true)}
                    className="btn-primary text-xs"
                  >
                    Finish &amp; Review
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Descriptive Question Box */}
          {activeTab === 'DESCRIPTIVE' && currentDesc && (
            <div className="card p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="font-mono text-xs font-semibold text-slate-500">
                  Descriptive Question {currentIndex + 1} of {session.descriptive_questions.length} (10 Marks)
                </span>
                <span className="badge-brand font-mono text-[10px] font-bold">10 Marks</span>
              </div>

              <h2 className="text-base font-bold text-slate-900 leading-snug">
                {currentDesc.question_text}
              </h2>

              <textarea
                value={descAnswers[currentDesc.id] || ''}
                onChange={(e) => setDescAnswers(prev => ({ ...prev, [currentDesc.id]: e.target.value }))}
                placeholder="Type your analytical answer notes, diagrams explanation, or code snippets here..."
                rows={8}
                className="input text-xs font-mono"
              />

              <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                <button
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex(i => i - 1)}
                  className="btn-secondary text-xs flex items-center gap-1"
                >
                  <ChevronLeft size={13} />
                  <span>Previous</span>
                </button>

                {currentIndex < session.descriptive_questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentIndex(i => i + 1)}
                    className="btn-primary text-xs flex items-center gap-1"
                  >
                    <span>Next</span>
                    <ChevronRight size={13} />
                  </button>
                ) : (
                  <button
                    onClick={() => setShowConfirmSubmit(true)}
                    className="btn-primary text-xs"
                  >
                    Finish &amp; Submit Mock
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Desktop Question Palette (Col 4) */}
        <div className="hidden md:block md:col-span-4 card p-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-slate-900">
            <span>Question Palette</span>
            <span className="font-mono text-[11px] text-slate-500">{answeredMcqsCount}/{totalMcqs} Answered</span>
          </div>

          <div className="grid grid-cols-5 gap-1.5 max-h-60 overflow-y-auto p-1">
            {session.mcqs.map((q, idx) => {
              const isAnswered = !!mcqAnswers[q.id];
              const isCurrent = activeTab === 'MCQ' && currentIndex === idx;
              const isMarked = !!mcqReviews[q.id];

              let pClass = "bg-slate-100 text-slate-700 border-slate-200";
              if (isCurrent) pClass = "bg-slate-900 text-white border-slate-900 font-bold ring-2 ring-blue-500";
              else if (isMarked) pClass = "bg-amber-100 text-amber-900 border-amber-300 font-semibold";
              else if (isAnswered) pClass = "bg-slate-900 text-white border-slate-900";

              return (
                <button
                  key={q.id}
                  onClick={() => { setActiveTab('MCQ'); setCurrentIndex(idx); }}
                  className={`p-1.5 rounded-md text-center font-mono text-xs border transition-colors ${pClass}`}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-100 space-y-2">
            <button
              onClick={() => setShowConfirmSubmit(true)}
              disabled={isSubmitting}
              className="btn-primary w-full text-xs font-bold py-2.5 justify-center shadow-sm"
            >
              {isSubmitting ? 'Submitting…' : 'Submit Examination'}
            </button>
          </div>
        </div>
      </main>

      {/* Mobile Question Palette Drawer */}
      {mobilePaletteOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex justify-end">
          <div className="w-72 bg-white h-full p-4 space-y-4 shadow-xl overflow-y-auto">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <h3 className="font-bold text-xs text-slate-900">Question Palette</h3>
              <button onClick={() => setMobilePaletteOpen(false)} className="p-1 text-slate-600">
                <X size={16} />
              </button>
            </div>

            <div className="grid grid-cols-5 gap-1.5">
              {session.mcqs.map((q, idx) => {
                const isAnswered = !!mcqAnswers[q.id];
                const isCurrent = activeTab === 'MCQ' && currentIndex === idx;
                const isMarked = !!mcqReviews[q.id];

                let pClass = "bg-slate-100 text-slate-700 border-slate-200";
                if (isCurrent) pClass = "bg-slate-900 text-white border-slate-900 font-bold";
                else if (isMarked) pClass = "bg-amber-100 text-amber-900 border-amber-300";
                else if (isAnswered) pClass = "bg-slate-900 text-white border-slate-900";

                return (
                  <button
                    key={q.id}
                    onClick={() => { setActiveTab('MCQ'); setCurrentIndex(idx); setMobilePaletteOpen(false); }}
                    className={`p-2 rounded text-center font-mono text-xs border transition-colors ${pClass}`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            <div className="pt-4 border-t border-slate-200">
              <button
                onClick={() => { setMobilePaletteOpen(false); setShowConfirmSubmit(true); }}
                disabled={isSubmitting}
                className="btn-primary w-full text-xs py-2.5 font-bold justify-center shadow-sm"
              >
                {isSubmitting ? 'Submitting…' : 'Submit Examination'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmSubmit && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl animate-fade-in">
            <h3 className="text-base font-bold text-slate-900">Submit Mock Examination?</h3>

            <div className="space-y-1 text-xs text-slate-600 font-medium">
              <p>• {answeredMcqsCount} of {totalMcqs} questions answered</p>
              {unansweredMcqsCount > 0 && (
                <p className="text-rose-600 font-semibold">• {unansweredMcqsCount} questions remain unanswered</p>
              )}
              {markedReviewCount > 0 && (
                <p className="text-amber-700 font-semibold">• {markedReviewCount} questions marked for review</p>
              )}
            </div>

            <div className="flex gap-3 justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowConfirmSubmit(false)}
                disabled={isSubmitting}
                className="btn-secondary text-xs"
              >
                Go Back &amp; Review
              </button>
              <button
                onClick={handleFinalSubmit}
                disabled={isSubmitting}
                className="btn-primary text-xs flex items-center gap-1.5"
              >
                {isSubmitting && <Spinner size="sm" />}
                <span>{isSubmitting ? 'Submitting…' : 'Confirm & Submit'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
