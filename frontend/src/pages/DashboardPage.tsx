import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play, AlertCircle, RotateCcw,
  ArrowRight, ChevronRight,
} from 'lucide-react';
import { progressApi, curriculumApi } from '../api';
import type { Dashboard, SubjectSummary } from '../types';
import { AppLayout } from '../components/layout';
import { DashboardSkeleton } from '../components/Skeleton';
import { ProgressBar } from '../components/ui';
import { useAuthStore } from '../stores/authStore';
import { useStudySessionStore } from '../stores/studySessionStore';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { activeSession, startSession } = useStudySessionStore();

  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [dash, subs] = await Promise.all([
        progressApi.getDashboard(),
        curriculumApi.getSubjects(),
      ]);
      setDashboard(dash);
      setSubjects(subs);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStartStudySession = () => {
    if (!activeSession) {
      startSession();
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <DashboardSkeleton />
      </AppLayout>
    );
  }

  const cont = dashboard?.continue_studying;
  const dueTopicsCount = dashboard?.revision_due_count || dashboard?.needs_revision_topics || 0;
  const weakTopicsCount = dashboard?.weak_topics?.length || 0;
  const firstName = user?.full_name?.split(' ')[0] || user?.username || 'Student';

  // Map progress per subject
  const subjectProgressMap: Record<number, number> = {};
  if (dashboard?.subjects) {
    dashboard.subjects.forEach(s => {
      subjectProgressMap[s.subject_id] = s.completion_percent;
    });
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto space-y-8 animate-fade-in text-slate-900 pb-12">
        {/* ── Greeting Header ── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold font-heading text-slate-900 tracking-tight">
              Good morning, {firstName}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Semester Study OS · Progress updated in real time
            </p>
          </div>

          <button
            onClick={handleStartStudySession}
            className="btn-primary text-xs flex items-center gap-1.5 self-start sm:self-auto"
          >
            <Play size={13} className="fill-white" />
            <span>{activeSession ? 'Resume Session' : 'Start Study Session'}</span>
          </button>
        </div>

        {/* ── 1. CONTINUE STUDYING HERO ── */}
        {cont && (
          <section className="space-y-2">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Continue Studying
            </div>

            <div className="card p-6 bg-white border border-slate-200 hover:border-slate-300 transition-all">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="badge-brand font-mono font-bold text-[10px]">
                      {cont.course_code} · Unit {cont.unit_number}
                    </span>
                    <span className="text-xs text-slate-500 font-medium">
                      {cont.last_studied_ago}
                    </span>
                  </div>

                  <h2 className="text-xl sm:text-2xl font-bold text-slate-900 leading-snug font-heading">
                    {cont.topic_name}
                  </h2>

                  <div className="flex items-center gap-3 text-xs text-slate-600">
                    <span>{cont.mastery_percent.toFixed(0)}% mastery</span>
                    <span>·</span>
                    <span>Next: <strong className="text-slate-900">{cont.next_action_label}</strong></span>
                  </div>
                </div>

                <div className="shrink-0 flex items-center">
                  <button
                    onClick={() => navigate(`/topics/${cont.topic_id}`)}
                    className="btn-primary text-xs py-2.5 px-5 flex items-center gap-2 shadow-sm"
                  >
                    <span>Continue</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ── 2. NEEDS ATTENTION ROW ── */}
        {(dueTopicsCount > 0 || weakTopicsCount > 0) && (
          <section className="space-y-2">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Needs Attention
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {dueTopicsCount > 0 && (
                <div
                  onClick={() => navigate('/revision')}
                  className="card p-4 hover:border-slate-300 cursor-pointer transition-all flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center shrink-0 border border-amber-200">
                      <RotateCcw size={16} />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-slate-900">
                        {dueTopicsCount} {dueTopicsCount === 1 ? 'Topic' : 'Topics'} Due for Revision
                      </div>
                      <div className="text-xs text-slate-500">Spaced repetition queue</div>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-slate-400" />
                </div>
              )}

              {weakTopicsCount > 0 && (
                <div
                  onClick={() => navigate('/mistakes')}
                  className="card p-4 hover:border-slate-300 cursor-pointer transition-all flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-rose-50 text-rose-700 flex items-center justify-center shrink-0 border border-rose-200">
                      <AlertCircle size={16} />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-slate-900">
                        {weakTopicsCount} {weakTopicsCount === 1 ? 'Topic' : 'Topics'} Need Practice
                      </div>
                      <div className="text-xs text-slate-500">Review mistakes notebook</div>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-slate-400" />
                </div>
              )}
            </div>
          </section>
        )}

        {/* ── 3. YOUR SUBJECTS LIST ── */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Your Subjects ({subjects.length})
            </div>
            <button
              onClick={() => navigate('/subjects')}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              <span>View All</span>
              <ChevronRight size={13} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {subjects.map((sub) => {
              const progressPct = subjectProgressMap[sub.id] || 0;
              return (
                <div
                  key={sub.id}
                  onClick={() => navigate(`/subjects/${sub.id}`)}
                  className="card p-4 hover:border-slate-300 cursor-pointer transition-all space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="badge-brand font-mono font-bold text-[10px]">
                        {sub.course_code}
                      </span>
                      <span className="text-xs font-bold font-mono text-slate-900">
                        {progressPct.toFixed(0)}%
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900 line-clamp-1">
                      {sub.name}
                    </h3>
                  </div>

                  <ProgressBar value={progressPct} size="sm" />
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
