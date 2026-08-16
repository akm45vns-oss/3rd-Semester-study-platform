import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RotateCcw, Check } from 'lucide-react';
import { practiceApi } from '../api';
import type { Mistake } from '../types';
import { Spinner, EmptyState } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function MistakesPage() {
  const [mistakes, setMistakes] = useState<Mistake[]>([]);
  const [filter, setFilter] = useState<'UNRESOLVED' | 'RESOLVED' | 'ALL'>('UNRESOLVED');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadMistakes = async () => {
    setLoading(true);
    try {
      const isResolvedParam = filter === 'UNRESOLVED' ? false : filter === 'RESOLVED' ? true : undefined;
      const data = await practiceApi.getMistakes(isResolvedParam);
      setMistakes(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMistakes();
  }, [filter]);

  const handleResolve = async (id: number) => {
    try {
      await practiceApi.resolveMistake(id);
      setMistakes(prev => prev.map(m => m.id === id ? { ...m, is_resolved: true } : m));
    } catch (e) {
      console.error(e);
    }
  };

  const unresolvedCount = mistakes.filter(m => !m.is_resolved).length;

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        <Breadcrumb items={[{ label: 'Home', to: '/dashboard' }, { label: 'Mistakes Notebook' }]} />

        {/* Top Header & Filter */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold font-heading text-slate-900">
              Mistakes Notebook
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {filter === 'UNRESOLVED'
                ? `${unresolvedCount} unresolved ${unresolvedCount === 1 ? 'concept gap' : 'concept gaps'} recorded during practice`
                : 'Review logged questions and error explanations'}
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
            {(['UNRESOLVED', 'RESOLVED', 'ALL'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
                  filter === tab
                    ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab === 'UNRESOLVED' ? 'Unresolved' : tab === 'RESOLVED' ? 'Resolved' : 'All'}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64"><Spinner size="lg" /></div>
        ) : mistakes.length === 0 ? (
          <EmptyState
            title={filter === 'UNRESOLVED' ? 'No Unresolved Mistakes' : 'No mistakes found'}
            description={filter === 'UNRESOLVED' ? 'You have cleared all logged errors from your practice drills.' : 'No logs match this filter.'}
            action={
              <button onClick={() => navigate('/practice')} className="btn-primary text-xs">
                Practice Questions
              </button>
            }
          />
        ) : (
          <div className="space-y-4">
            {mistakes.map(m => (
              <div key={m.id} className="card p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between gap-2 pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    {m.course_code && (
                      <span className="badge-brand font-mono font-bold text-[10px]">
                        {m.course_code}
                      </span>
                    )}
                    <span className="text-xs font-semibold text-slate-800">
                      {m.topic_name || 'Concept Gap'}
                    </span>
                  </div>

                  <span className={m.is_resolved ? 'badge-success' : 'badge-warning'}>
                    {m.is_resolved ? '✓ Resolved' : 'Needs Review'}
                  </span>
                </div>

                <h3 className="text-sm sm:text-base font-bold text-slate-900 leading-snug">
                  {m.description}
                </h3>

                {m.correction && (
                  <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 space-y-1">
                    <div className="font-bold text-emerald-800">Explanation &amp; Correction:</div>
                    <p className="leading-relaxed">{m.correction}</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                  <button
                    onClick={() => navigate(`/topics/${m.topic_id}`)}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
                  >
                    <RotateCcw size={12} />
                    <span>Review Topic Theory</span>
                  </button>

                  {!m.is_resolved && (
                    <button
                      onClick={() => handleResolve(m.id)}
                      className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
                    >
                      <Check size={12} />
                      <span>Mark Resolved</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
