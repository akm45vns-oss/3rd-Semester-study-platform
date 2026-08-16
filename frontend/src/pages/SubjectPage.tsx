import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BookOpen, FlaskConical, ChevronRight, ChevronDown, ChevronUp,
  CheckCircle2,
} from 'lucide-react';
import { curriculumApi, progressApi, intelligenceApi } from '../api';
import type { Subject, Unit, Topic, TopicProgress, SubjectProgress, PracticalItem } from '../types';
import { ProgressBar, StatusBadge, Spinner } from '../components/ui';
import { AppLayout, Breadcrumb } from '../components/layout';

function TopicRow({
  topic,
  progress,
  onClick,
}: {
  topic: Topic;
  progress: TopicProgress | undefined;
  onClick: () => void;
}) {
  const status = progress?.status ?? 'NOT_STARTED';
  const mastery = progress?.mastery_percent ?? 0;

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100
                 transition-colors text-left group border border-transparent hover:border-slate-200"
    >
      <div className="w-4 h-4 shrink-0 flex items-center justify-center">
        {status === 'LEARNED' ? (
          <CheckCircle2 size={15} className="text-emerald-600" />
        ) : status === 'LEARNING' ? (
          <div className="w-3 h-3 rounded-full border-2 border-blue-600" />
        ) : status === 'NEEDS_REVISION' ? (
          <div className="w-3 h-3 rounded-full border-2 border-amber-600" />
        ) : (
          <div className="w-2.5 h-2.5 rounded-full border border-slate-300" />
        )}
      </div>
      <span className="flex-1 text-xs font-semibold text-slate-800 truncate">
        {topic.name}
      </span>
      {mastery > 0 && (
        <span className="text-[11px] font-mono font-bold text-slate-500 shrink-0">{mastery.toFixed(0)}%</span>
      )}
      <StatusBadge status={status} />
      <ChevronRight size={13} className="text-slate-400 group-hover:text-slate-900 transition-transform shrink-0" />
    </button>
  );
}

function UnitSection({
  unit,
  progressMap,
  onTopicClick,
  defaultExpanded = false,
}: {
  unit: Unit;
  progressMap: Record<number, TopicProgress>;
  onTopicClick: (topicId: number) => void;
  defaultExpanded?: boolean;
}) {
  const [open, setOpen] = useState(defaultExpanded);
  const learnedCount = unit.topics.filter(t => progressMap[t.id]?.status === 'LEARNED').length;
  const total = unit.topics.length;
  const unitPct = total > 0 ? (learnedCount / total) * 100 : 0;

  return (
    <div className="card p-4 space-y-3">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 group text-left"
        aria-expanded={open}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 text-slate-800 text-[11px] font-mono font-bold rounded-md">
                Unit {unit.unit_number}
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                {unit.name}
              </h3>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs text-slate-500 font-medium">{learnedCount}/{total} topics</span>
              {open ? <ChevronUp size={16} className="text-slate-600" /> : <ChevronDown size={16} className="text-slate-600" />}
            </div>
          </div>
          <ProgressBar value={unitPct} size="sm" />
        </div>
      </button>

      {open && (
        <div className="pt-2 border-t border-slate-100 space-y-1">
          {unit.topics.map(topic => (
            <TopicRow
              key={topic.id}
              topic={topic}
              progress={progressMap[topic.id]}
              onClick={() => onTopicClick(topic.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function PracticalRow({
  practical,
  onClick,
}: {
  practical: PracticalItem;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="card p-4 hover:border-slate-300 w-full text-left flex items-center justify-between gap-3 transition-all"
    >
      <div className="space-y-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="badge-brand font-mono font-bold text-[10px]">
            Exp #{practical.practical_number}
          </span>
          <StatusBadge status={practical.status} />
        </div>
        <h4 className="text-sm font-bold text-slate-900 line-clamp-1">
          {practical.title}
        </h4>
        {practical.objective && (
          <p className="text-xs text-slate-500 line-clamp-1">{practical.objective}</p>
        )}
      </div>

      <ChevronRight size={16} className="text-slate-400 shrink-0" />
    </button>
  );
}

export default function SubjectPage() {
  const { id } = useParams<{ id: string }>();
  const subjectId = Number(id);
  const navigate = useNavigate();

  const [subject, setSubject] = useState<Subject | null>(null);
  const [topicProgress] = useState<Record<number, TopicProgress>>({});
  const [subjectProgress, setSubjectProgress] = useState<SubjectProgress | null>(null);
  const [practicals, setPracticals] = useState<PracticalItem[]>([]);
  const [activeTab, setActiveTab] = useState<'UNITS' | 'PRACTICALS'>('UNITS');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      curriculumApi.getSubject(subjectId),
      progressApi.getSubjectProgress(subjectId),
      intelligenceApi.getAllPracticals(subjectId).catch(() => []),
    ]).then(([sub, prog, pracs]) => {
      setSubject(sub);
      setSubjectProgress(prog);
      setPracticals(pracs);
    }).finally(() => setLoading(false));
  }, [subjectId]);

  if (loading || !subject) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  const completionPct = subjectProgress?.completion_percent ?? 0;

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in text-slate-900 pb-12">
        <Breadcrumb items={[
          { label: 'Subjects', to: '/subjects' },
          { label: subject.course_code },
        ]} />

        {/* ── Subject Banner Card ── */}
        <div className="card p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="badge-brand font-mono font-bold text-xs">{subject.course_code}</span>
                <span className="text-xs text-slate-500 font-medium">{subject.credits} Credits · 6 Units</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 font-heading">
                {subject.name}
              </h1>
              {subject.description && (
                <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">{subject.description}</p>
              )}
            </div>

            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-right shrink-0">
              <div className="text-2xl font-bold font-mono text-slate-900 leading-none">
                {completionPct.toFixed(0)}%
              </div>
              <div className="text-[10px] font-semibold text-slate-500 mt-1">Overall Completion</div>
            </div>
          </div>

          <ProgressBar value={completionPct} size="md" />

          {/* Tab Selector */}
          <div className="flex gap-2 pt-2 border-t border-slate-100">
            <button
              onClick={() => setActiveTab('UNITS')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'UNITS'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <BookOpen size={13} />
              <span>Syllabus Units ({subject.units.length})</span>
            </button>

            {practicals.length > 0 && (
              <button
                onClick={() => setActiveTab('PRACTICALS')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'PRACTICALS'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <FlaskConical size={13} />
                <span>Lab Practicals ({practicals.length})</span>
              </button>
            )}
          </div>
        </div>

        {/* ── Content View ── */}
        {activeTab === 'UNITS' ? (
          <div className="space-y-3">
            {subject.units.map((unit, idx) => (
              <UnitSection
                key={unit.id}
                unit={unit}
                progressMap={topicProgress}
                onTopicClick={(tId) => navigate(`/topics/${tId}`)}
                defaultExpanded={idx === 0}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {practicals.map((prac) => (
              <PracticalRow
                key={prac.id}
                practical={prac}
                onClick={() => navigate(`/practicals?practical_id=${prac.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
