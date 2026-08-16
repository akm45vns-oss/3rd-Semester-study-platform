import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BookOpen, HelpCircle, Code2, RotateCcw,
  ChevronRight, ChevronLeft, ArrowRight,
} from 'lucide-react';
import { progressApi, practiceApi } from '../api';
import type { TopicWorkspace, Question, TopicStatus } from '../types';
import { StatusBadge } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';
import { MarkdownViewer } from '../components/MarkdownViewer';
import { TopicWorkspaceSkeleton } from '../components/Skeleton';

export default function TopicPage() {
  const { id } = useParams<{ id: string }>();
  const topicId = Number(id);
  const navigate = useNavigate();

  const [workspace, setWorkspace] = useState<TopicWorkspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);

  const loadWorkspace = useCallback(async () => {
    try {
      setLoading(true);
      const ws = await progressApi.getTopicWorkspace(topicId);
      setWorkspace(ws);

      // Load available questions count
      const qs = await practiceApi.getQuestions({ topic_id: topicId });
      setQuestions(qs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    loadWorkspace();
  }, [topicId, loadWorkspace]);

  const handleUpdateStatus = async (status: TopicStatus) => {
    if (!workspace) return;
    try {
      const updated = await progressApi.updateTopicProgress(topicId, { status, notes_read: true });
      setWorkspace(prev => prev ? { ...prev, progress: updated } : null);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !workspace) {
    return (
      <AppLayout>
        <TopicWorkspaceSkeleton />
      </AppLayout>
    );
  }

  const { topic, unit, subject, notes, progress, coding_problem, next_topic, prev_topic } = workspace;
  const theoryNotes = notes.length > 0 ? notes[0].content : '';

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-16">
        {/* Top Breadcrumb */}
        <Breadcrumb items={[
          { label: 'Subjects', to: '/subjects' },
          { label: subject.course_code, to: `/subjects/${subject.id}` },
          { label: `Unit ${unit.unit_number}` },
          { label: topic.name },
        ]} />

        {/* ── Topic Header (Clean Editorial Style) ── */}
        <header className="card p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="badge-brand font-mono font-bold text-xs">{subject.course_code}</span>
                <span className="text-xs font-semibold text-slate-500">Unit {unit.unit_number} · {unit.name}</span>
                <StatusBadge status={progress.status} />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 font-heading leading-snug">
                {topic.name}
              </h1>
              {topic.description && (
                <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">{topic.description}</p>
              )}
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-right shrink-0">
              <div className="text-xl font-bold font-mono text-slate-900 leading-none">
                {progress.mastery_percent.toFixed(0)}%
              </div>
              <div className="text-[10px] font-semibold text-slate-500 mt-1">Topic Mastery</div>
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center gap-2 pt-3 border-t border-slate-100 flex-wrap">
            {questions.length > 0 && (
              <button
                onClick={() => navigate(`/practice?subject_id=${subject.id}&unit_id=${unit.id}`)}
                className="btn-primary text-xs flex items-center gap-1.5"
              >
                <HelpCircle size={13} />
                <span>Practice Questions ({questions.length})</span>
                <ArrowRight size={13} />
              </button>
            )}

            {coding_problem && (
              <button
                onClick={() => navigate(`/coding?mode=practice&problem_id=${coding_problem.id}`)}
                className="btn-secondary text-xs flex items-center gap-1.5"
              >
                <Code2 size={13} />
                <span>Coding Challenge</span>
              </button>
            )}

            <button
              onClick={() => handleUpdateStatus('NEEDS_REVISION')}
              className="text-xs font-medium text-slate-600 hover:text-slate-900 px-2.5 py-1.5 hover:bg-slate-100 rounded-md transition-colors flex items-center gap-1"
            >
              <RotateCcw size={12} />
              <span>Revise Later</span>
            </button>
          </div>
        </header>

        {/* ── Core Digital Textbook Content ── */}
        <article className="card p-6 sm:p-8 space-y-6">
          {theoryNotes ? (
            <div className="max-w-[70ch]">
              <MarkdownViewer content={theoryNotes} topicTitle={topic.name} />
            </div>
          ) : (
            <div className="py-12 text-center space-y-3 text-slate-500">
              <BookOpen size={36} className="mx-auto text-slate-400" />
              <h3 className="text-base font-bold text-slate-900">No notes recorded yet</h3>
              <p className="text-xs max-w-sm mx-auto">This topic syllabus reference is registered in StudyForge.</p>
            </div>
          )}
        </article>

        {/* ── Bottom Prev / Next Navigation ── */}
        <footer className="flex items-center justify-between gap-3 pt-2">
          {prev_topic ? (
            <button
              onClick={() => navigate(`/topics/${prev_topic.id}`)}
              className="btn-secondary text-xs flex items-center gap-1.5"
            >
              <ChevronLeft size={14} />
              <span className="truncate max-w-[150px] sm:max-w-[220px]">Prev: {prev_topic.name}</span>
            </button>
          ) : <div />}

          {next_topic ? (
            <button
              onClick={() => navigate(`/topics/${next_topic.id}`)}
              className="btn-primary text-xs flex items-center gap-1.5"
            >
              <span className="truncate max-w-[150px] sm:max-w-[220px]">Next: {next_topic.name}</span>
              <ChevronRight size={14} />
            </button>
          ) : <div />}
        </footer>
      </div>
    </AppLayout>
  );
}
