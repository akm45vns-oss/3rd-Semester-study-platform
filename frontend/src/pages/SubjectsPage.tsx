import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { curriculumApi, progressApi } from '../api';
import type { SubjectSummary, SubjectProgress } from '../types';
import { ProgressBar, Spinner, EmptyState } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [progress, setProgress] = useState<Record<number, SubjectProgress>>({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    curriculumApi.getSubjects().then(async (subs) => {
      setSubjects(subs);
      const progMap: Record<number, SubjectProgress> = {};
      await Promise.all(
        subs.map(async (s) => {
          try {
            progMap[s.id] = await progressApi.getSubjectProgress(s.id);
          } catch { /* ignore */ }
        })
      );
      setProgress(progMap);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-12">
        <Breadcrumb items={[{ label: 'Home', to: '/dashboard' }, { label: 'Subjects' }]} />

        <div className="pb-2 border-b border-slate-200">
          <h1 className="text-2xl font-bold font-heading text-slate-900">
            Subjects
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            5 core semester subjects · 30 units · Complete syllabus
          </p>
        </div>

        {subjects.length === 0 ? (
          <EmptyState
            title="No subjects found"
            description="The curriculum has not been loaded. Please check database connection."
          />
        ) : (
          <div className="space-y-3">
            {subjects.map((s) => {
              const sp = progress[s.id];
              const pct = sp ? sp.completion_percent : 0;
              const unitsStudied = sp ? Math.round((pct / 100) * 6) : 0;

              return (
                <div
                  key={s.id}
                  className="card p-5 hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="badge-brand font-mono font-bold text-[10px]">
                        {s.course_code}
                      </span>
                      <span className="text-xs text-slate-500 font-medium">
                        {s.credits} Credits · 6 Units
                      </span>
                    </div>

                    <h2 className="text-base sm:text-lg font-bold text-slate-900 font-heading">
                      {s.name}
                    </h2>

                    <div className="flex items-center gap-3 text-xs text-slate-600">
                      <span className="font-semibold text-slate-900">{pct.toFixed(0)}% complete</span>
                      <span>·</span>
                      <span>{unitsStudied} of 6 units studied</span>
                      {sp && sp.learned_topics > 0 && (
                        <>
                          <span>·</span>
                          <span className="text-emerald-700 font-medium">{sp.learned_topics} topics mastered</span>
                        </>
                      )}
                    </div>

                    <div className="max-w-xs pt-1">
                      <ProgressBar value={pct} size="sm" />
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center">
                    <button
                      onClick={() => navigate(`/subjects/${s.id}`)}
                      className="btn-secondary text-xs py-2 px-4 flex items-center gap-1.5 w-full sm:w-auto justify-center"
                    >
                      <span>Open Subject</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
