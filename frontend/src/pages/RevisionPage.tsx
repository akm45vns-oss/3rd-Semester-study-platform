import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, ArrowRight, Check } from 'lucide-react';
import { intelligenceApi } from '../api';
import type { RevisionQueueItem } from '../types';
import { Spinner, EmptyState } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function RevisionPage() {
  const [items, setItems] = useState<RevisionQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const navigate = useNavigate();

  const loadQueue = async () => {
    setLoading(true);
    try {
      const data = await intelligenceApi.getRevisionQueue();
      setItems(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleCompleteRevision = async (topicId: number) => {
    setProcessingId(topicId);
    try {
      await intelligenceApi.completeRevision(topicId);
      setItems(prev => prev.filter(i => i.topic_id !== topicId));
    } catch (e) {
      console.error(e);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        <Breadcrumb items={[{ label: 'Home', to: '/dashboard' }, { label: 'Revision Queue' }]} />

        {/* Top Header */}
        <div className="pb-2 border-b border-slate-200">
          <h1 className="text-xl sm:text-2xl font-bold font-heading text-slate-900">
            Revision Queue
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {items.length > 0
              ? `${items.length} ${items.length === 1 ? 'topic' : 'topics'} scheduled for spaced repetition review`
              : 'Keep concepts fresh in long-term memory'}
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64"><Spinner size="lg" /></div>
        ) : items.length === 0 ? (
          <EmptyState
            title="You're all caught up!"
            description="No topics are currently due for spaced repetition revision. Keep studying new topics to add them to your revision calendar."
            action={
              <button onClick={() => navigate('/subjects')} className="btn-primary text-xs">
                Browse Curriculum
              </button>
            }
          />
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.topic_id}
                className="card p-5 hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="badge-brand font-mono font-bold text-[10px]">
                      {item.course_code} · Unit {item.unit_number}
                    </span>
                    <span className="text-xs text-slate-500 font-medium flex items-center gap-1">
                      <Clock size={11} className="text-slate-400" />
                      {item.last_studied_at ? `Last studied ${new Date(item.last_studied_at).toLocaleDateString()}` : 'Due for Review'}
                    </span>
                    <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                      {item.mastery_percent.toFixed(0)}% Mastery
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 font-heading">
                    {item.topic_name}
                  </h3>

                  <p className="text-xs text-slate-500">
                    {item.reason}
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleCompleteRevision(item.topic_id)}
                    disabled={processingId === item.topic_id}
                    className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1"
                    title="Mark topic revision complete"
                  >
                    <Check size={12} />
                    <span>Done</span>
                  </button>

                  <button
                    onClick={() => navigate(`/topics/${item.topic_id}`)}
                    className="btn-primary text-xs py-1.5 px-3.5 flex items-center gap-1.5"
                  >
                    <span>Quick Revision</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
