import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  CheckCircle2, XCircle, Clock,
  ArrowRight, ArrowLeft, Award,
} from 'lucide-react';
import { practiceApi, curriculumApi } from '../api';
import type { Question, TestSession, TestResult, SubjectSummary, Unit } from '../types';
import { Spinner } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function PracticeQuizPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<'SELECT' | 'PRACTICE' | 'TEST' | 'RESULT'>('SELECT');
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);

  // Selection
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | ''>('');
  const [selectedUnitId, setSelectedUnitId] = useState<number | ''>('');
  const [practiceModeType, setPracticeModeType] = useState<'PRACTICE' | 'TEST'>('PRACTICE');

  // Test Mode Session State
  const [testSession, setTestSession] = useState<TestSession | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [testAnswers, setTestAnswers] = useState<Record<number, number>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(false);

  // Practice Mode State (Immediate Feedback)
  const [practiceQuestions, setPracticeQuestions] = useState<Question[]>([]);
  const [practiceIndex, setPracticeIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [practiceScore, setPracticeScore] = useState(0);

  useEffect(() => {
    curriculumApi.getSubjects().then((subs) => {
      setSubjects(subs);
      if (subs.length > 0) {
        const initSubId = searchParams.get('subject_id') ? Number(searchParams.get('subject_id')) : subs[0].id;
        setSelectedSubjectId(initSubId);
      }
    });
  }, [searchParams]);

  useEffect(() => {
    if (selectedSubjectId) {
      curriculumApi.getSubjectUnits(Number(selectedSubjectId)).then((uList) => {
        setUnits(uList);
        const urlUnitId = searchParams.get('unit_id');
        if (urlUnitId) {
          setSelectedUnitId(Number(urlUnitId));
        } else {
          setSelectedUnitId(''); // Default to All Units
        }
      });
    }
  }, [selectedSubjectId, searchParams]);

  // Test Mode Countdown
  useEffect(() => {
    if (phase !== 'TEST' || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(interval);
          handleSubmitTest();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [phase, timeLeft]);

  // Start Action
  const handleStart = async () => {
    setLoading(true);
    try {
      if (practiceModeType === 'PRACTICE') {
        const qs = await practiceApi.getQuestions({
          subject_id: selectedSubjectId ? Number(selectedSubjectId) : undefined,
          unit_id: selectedUnitId ? Number(selectedUnitId) : undefined,
        });
        if (qs.length === 0) {
          alert('No questions available for this selection. Try selecting all units.');
          return;
        }
        setPracticeQuestions(qs.slice(0, 10));
        setPracticeIndex(0);
        setSelectedOptionId(null);
        setIsAnswered(false);
        setPracticeScore(0);
        setPhase('PRACTICE');
      } else {
        const session = await practiceApi.generateTest({
          scope: selectedUnitId ? 'UNIT' : 'SUBJECT',
          subject_id: selectedSubjectId ? Number(selectedSubjectId) : undefined,
          unit_id: selectedUnitId ? Number(selectedUnitId) : undefined,
          question_count: 10,
        });
        setTestSession(session);
        setCurrentIndex(0);
        setTestAnswers({});
        setTimeLeft((session.time_limit_minutes || 10) * 60);
        setPhase('TEST');
      }
    } catch (e) {
      console.error(e);
      alert('Failed to start practice. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePracticeSelect = (optionId: number) => {
    if (isAnswered) return;
    setSelectedOptionId(optionId);
    setIsAnswered(true);

    const currentQ = practiceQuestions[practiceIndex];
    const chosen = currentQ.options.find(o => o.id === optionId);
    if (chosen?.is_correct) {
      setPracticeScore(s => s + 1);
    }

    practiceApi.submitAttempt({
      question_id: currentQ.id,
      selected_option_id: optionId,
      time_taken_seconds: 5,
    }).catch(console.error);
  };

  const handleNextPracticeQuestion = () => {
    if (practiceIndex < practiceQuestions.length - 1) {
      setPracticeIndex(i => i + 1);
      setSelectedOptionId(null);
      setIsAnswered(false);
    } else {
      setPhase('RESULT');
    }
  };

  const handleTestAnswer = (qId: number, optId: number) => {
    setTestAnswers(prev => ({ ...prev, [qId]: optId }));
  };

  const handleSubmitTest = async () => {
    if (!testSession) return;
    setLoading(true);
    try {
      const answers = Object.entries(testAnswers).map(([qId, optId]) => ({
        question_id: Number(qId),
        selected_option_id: optId,
      }));
      const res = await practiceApi.submitTest({
        session_id: testSession.session_id,
        scope: testSession.scope,
        answers,
      });
      setTestResult(res);
      setPhase('RESULT');
    } catch (e) {
      console.error(e);
      alert('Failed to submit test.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        <Breadcrumb items={[
          { label: 'Home', to: '/dashboard' },
          { label: 'Practice & Quizzes' }
        ]} />

        {/* ── 1. SELECTION PHASE ── */}
        {phase === 'SELECT' && (
          <div className="card p-6 sm:p-8 space-y-6">
            <div className="pb-3 border-b border-slate-200">
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 font-heading">
                Practice Questions
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Choose a subject and unit to practice questions with immediate feedback.
              </p>
            </div>

            {/* Step 1: Subject */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                1. Select Subject
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {subjects.map(s => (
                  <button
                    key={s.id}
                    onClick={() => setSelectedSubjectId(s.id)}
                    className={`p-3 rounded-lg border text-left text-xs transition-all flex items-center justify-between ${
                      selectedSubjectId === s.id
                        ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                        : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    <span className="truncate">{s.name}</span>
                    <span className="font-mono text-[10px] opacity-75">{s.course_code}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Step 2: Unit */}
            {selectedSubjectId && (
              <div className="space-y-2">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                  2. Select Unit
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    onClick={() => setSelectedUnitId('')}
                    className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                      selectedUnitId === ''
                        ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                        : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    All Units (Entire Syllabus)
                  </button>
                  {units.map(u => (
                    <button
                      key={u.id}
                      onClick={() => setSelectedUnitId(u.id)}
                      className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                        selectedUnitId === u.id
                          ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                          : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                      }`}
                    >
                      Unit {u.unit_number}: {u.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Step 3: Mode */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                3. Choose Mode
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setPracticeModeType('PRACTICE')}
                  className={`p-3.5 rounded-lg border text-left space-y-1 transition-all ${
                    practiceModeType === 'PRACTICE'
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                  }`}
                >
                  <div className="font-semibold text-xs">Practice Mode</div>
                  <div className="text-[11px] opacity-80 leading-relaxed">Instant feedback and explanations per question</div>
                </button>

                <button
                  onClick={() => setPracticeModeType('TEST')}
                  className={`p-3.5 rounded-lg border text-left space-y-1 transition-all ${
                    practiceModeType === 'TEST'
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                  }`}
                >
                  <div className="font-semibold text-xs">Timed Test Mode</div>
                  <div className="text-[11px] opacity-80 leading-relaxed">Timed 10-question evaluation with grade report</div>
                </button>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={handleStart}
                disabled={loading || !selectedSubjectId}
                className="btn-primary w-full text-xs py-3 font-semibold justify-center"
              >
                {loading ? <Spinner size="sm" /> : <span>Start Practice →</span>}
              </button>
            </div>
          </div>
        )}

        {/* ── 2. PRACTICE MODE (Immediate Feedback) ── */}
        {phase === 'PRACTICE' && practiceQuestions.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 pb-1">
              <span className="font-semibold text-slate-800">
                Question {practiceIndex + 1} of {practiceQuestions.length}
              </span>
              <span className="font-mono font-semibold text-slate-600">
                Score: {practiceScore} / {practiceIndex + (isAnswered ? 1 : 0)}
              </span>
            </div>

            {(() => {
              const q = practiceQuestions[practiceIndex];
              return (
                <div className="card p-6 sm:p-7 space-y-5">
                  <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                    {q.question_text}
                  </h2>

                  <div className="space-y-2.5">
                    {q.options.map((opt, idx) => {
                      const isChosen = selectedOptionId === opt.id;
                      let btnStyle = "bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-800";

                      if (isAnswered) {
                        if (opt.is_correct) {
                          btnStyle = "bg-emerald-50 border-emerald-500 text-emerald-900 font-semibold";
                        } else if (isChosen && !opt.is_correct) {
                          btnStyle = "bg-rose-50 border-rose-500 text-rose-900 font-semibold";
                        } else {
                          btnStyle = "bg-slate-50 border-slate-200 text-slate-400 opacity-60";
                        }
                      }

                      return (
                        <button
                          key={opt.id}
                          onClick={() => handlePracticeSelect(opt.id)}
                          disabled={isAnswered}
                          className={`w-full p-3.5 rounded-lg border text-left text-xs flex items-center justify-between transition-all ${btnStyle}`}
                        >
                          <div className="flex items-center gap-3">
                            <span className="w-5 h-5 rounded flex items-center justify-center font-mono font-bold text-[10px] bg-white border border-slate-200 text-slate-700">
                              {String.fromCharCode(65 + idx)}
                            </span>
                            <span>{opt.option_text}</span>
                          </div>

                          {isAnswered && opt.is_correct && (
                            <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                          )}
                          {isAnswered && isChosen && !opt.is_correct && (
                            <XCircle size={16} className="text-rose-600 shrink-0" />
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Immediate Explanation on Selection */}
                  {isAnswered && (
                    <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-800 space-y-1.5 animate-fade-in">
                      <div className="font-bold text-slate-900">Explanation</div>
                      <p className="leading-relaxed text-slate-600">
                        {q.explanation || 'Option chosen is verified against university curriculum syllabus.'}
                      </p>
                    </div>
                  )}

                  {isAnswered && (
                    <div className="pt-2 flex justify-end">
                      <button
                        onClick={handleNextPracticeQuestion}
                        className="btn-primary text-xs py-2.5 px-5 flex items-center gap-2"
                      >
                        <span>{practiceIndex < practiceQuestions.length - 1 ? 'Next Question' : 'Complete Practice'}</span>
                        <ArrowRight size={13} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        )}

        {/* ── 3. TIMED TEST MODE ── */}
        {phase === 'TEST' && testSession && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 pb-1">
              <span className="font-semibold text-slate-800">
                Question {currentIndex + 1} of {testSession.questions.length}
              </span>
              <div className="flex items-center gap-1.5 font-mono font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
                <Clock size={13} />
                <span>{Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</span>
              </div>
            </div>

            {(() => {
              const q = testSession.questions[currentIndex];
              const selectedOpt = testAnswers[q.id];

              return (
                <div className="card p-6 sm:p-7 space-y-5">
                  <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                    {q.question_text}
                  </h2>

                  <div className="space-y-2.5">
                    {q.options.map((opt, idx) => {
                      const isSelected = selectedOpt === opt.id;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => handleTestAnswer(q.id, opt.id)}
                          className={`w-full p-3.5 rounded-lg border text-left text-xs flex items-center justify-between transition-all ${
                            isSelected
                              ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                              : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-800'
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
                          {isSelected && <CheckCircle2 size={15} className="text-white" />}
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
                      <ArrowLeft size={13} />
                      <span>Previous</span>
                    </button>

                    {currentIndex < testSession.questions.length - 1 ? (
                      <button
                        onClick={() => setCurrentIndex(i => i + 1)}
                        className="btn-primary text-xs flex items-center gap-1"
                      >
                        <span>Next</span>
                        <ArrowRight size={13} />
                      </button>
                    ) : (
                      <button
                        onClick={handleSubmitTest}
                        disabled={loading}
                        className="btn-primary text-xs py-2 px-4"
                      >
                        {loading ? <Spinner size="sm" /> : 'Finish & Submit Test'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* ── 4. RESULTS PHASE ── */}
        {phase === 'RESULT' && (
          <div className="card p-8 space-y-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-slate-900 text-white flex items-center justify-center mx-auto shadow-sm">
              <Award size={24} />
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-900 font-heading">Practice Complete</h2>
              <div className="text-3xl font-bold text-slate-900 font-mono mt-1">
                {testResult
                  ? `${testResult.score_percentage.toFixed(0)}%`
                  : `${Math.round((practiceScore / (practiceQuestions.length || 1)) * 100)}%`}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {testResult
                  ? `${testResult.correct_count} of ${testResult.total_questions} questions correct`
                  : `${practiceScore} of ${practiceQuestions.length} questions correct`}
              </p>
            </div>

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => navigate('/mistakes')}
                className="btn-secondary text-xs py-2 px-4"
              >
                Review Mistakes
              </button>
              <button
                onClick={() => setPhase('SELECT')}
                className="btn-primary text-xs py-2 px-4"
              >
                Practice Another Topic
              </button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
