import { useEffect, useState } from 'react';
import { Save, X } from 'lucide-react';
import { intelligenceApi, progressApi, curriculumApi } from '../api';
import type { PracticalItem, SubjectSummary } from '../types';
import { StatusBadge, Spinner, EmptyState } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

export default function PracticalsPage() {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [practicals, setPracticals] = useState<PracticalItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Edit Evidence Modal State
  const [editingItem, setEditingItem] = useState<PracticalItem | null>(null);
  const [codeContent, setCodeContent] = useState('');
  const [outputNotes, setOutputNotes] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    curriculumApi.getSubjects().then((subs) => {
      setSubjects(subs);
      if (subs.length > 0) {
        setSelectedSubjectId(subs[0].id);
      }
    });
  }, []);

  const loadPracticals = async () => {
    setLoading(true);
    try {
      const data = await intelligenceApi.getAllPracticals(selectedSubjectId || undefined);
      setPracticals(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedSubjectId !== null) {
      loadPracticals();
    }
  }, [selectedSubjectId]);

  const handleOpenEdit = (item: PracticalItem) => {
    setEditingItem(item);
    setCodeContent(item.code_content || '');
    setOutputNotes(item.output_notes || '');
  };

  const handleSaveEvidence = async () => {
    if (!editingItem) return;
    setSaving(true);
    try {
      await progressApi.updatePracticalProgress(editingItem.id, {
        code_content: codeContent,
        output_notes: outputNotes,
        status: 'COMPLETED',
      });
      setPracticals(prev => prev.map(p => p.id === editingItem.id ? {
        ...p,
        code_content: codeContent,
        output_notes: outputNotes,
        status: 'COMPLETED',
      } : p));
      setEditingItem(null);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const total = practicals.length;
  const completed = practicals.filter(p => p.status === 'COMPLETED').length;
  const pct = total > 0 ? (completed / total) * 100 : 0;

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        <Breadcrumb items={[{ label: 'Home', to: '/dashboard' }, { label: 'Lab Practicals' }]} />

        {/* Top Header & Progress */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold font-heading text-slate-900">
              Lab Practicals &amp; Experiments
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Track university lab submissions and code verification
            </p>
          </div>

          <div className="text-right">
            <span className="font-mono text-xs font-bold text-slate-900">
              {completed} / {total} Completed ({pct.toFixed(0)}%)
            </span>
          </div>
        </div>

        {/* Subject Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {subjects.map(s => (
            <button
              key={s.id}
              onClick={() => setSelectedSubjectId(s.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                selectedSubjectId === s.id
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {s.course_code} · {s.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64"><Spinner size="lg" /></div>
        ) : practicals.length === 0 ? (
          <EmptyState
            title="No practicals recorded"
            description="No practical experiments are listed for this subject syllabus."
          />
        ) : (
          <div className="space-y-3">
            {practicals.map((p) => (
              <div key={p.id} className="card p-5 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="badge-brand font-mono font-bold text-[10px]">
                        Experiment #{p.practical_number}
                      </span>
                      {p.course_code && (
                        <span className="text-xs font-mono font-semibold text-slate-500">{p.course_code}</span>
                      )}
                      <StatusBadge status={p.status} />
                    </div>

                    <h3 className="text-base font-bold text-slate-900 font-heading">
                      {p.title}
                    </h3>
                  </div>

                  <button
                    onClick={() => handleOpenEdit(p)}
                    className="btn-secondary text-xs py-1.5 px-3 shrink-0"
                  >
                    {p.code_content ? 'Edit Solution' : 'Submit Solution'}
                  </button>
                </div>

                {p.objective && (
                  <div className="text-xs text-slate-600 leading-relaxed">
                    <span className="font-semibold text-slate-900">Aim: </span>
                    {p.objective}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ── Edit Evidence Modal ── */}
        {editingItem && (
          <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white border border-slate-200 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-xl animate-fade-in max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <div>
                  <span className="text-[10px] font-mono font-bold text-slate-500">Exp #{editingItem.practical_number}</span>
                  <h3 className="text-base font-bold text-slate-900">{editingItem.title}</h3>
                </div>
                <button onClick={() => setEditingItem(null)} className="p-1 text-slate-400 hover:text-slate-700">
                  <X size={18} />
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Source Code / Solution Script:
                  </label>
                  <textarea
                    rows={8}
                    value={codeContent}
                    onChange={e => setCodeContent(e.target.value)}
                    placeholder="// Paste your verified practical code here..."
                    className="input font-mono text-xs"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Output Verification &amp; Notes:
                  </label>
                  <textarea
                    rows={3}
                    value={outputNotes}
                    onChange={e => setOutputNotes(e.target.value)}
                    placeholder="Terminal execution output, test cases passed, or faculty sign-off notes..."
                    className="input font-mono text-xs"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  onClick={() => setEditingItem(null)}
                  className="btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEvidence}
                  disabled={saving}
                  className="btn-primary text-xs flex items-center gap-1.5"
                >
                  {saving ? <Spinner size="sm" /> : <Save size={13} />}
                  <span>Save Practical</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
