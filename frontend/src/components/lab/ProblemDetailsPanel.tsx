import { type FC, useState } from 'react';
import { HelpCircle, RotateCcw, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';
import type { CodingProblem } from '../../types';

interface ProblemDetailsPanelProps {
  problem: CodingProblem;
  onResetStarterCode: () => void;
  onSubmit: () => void;
  isSubmitting: boolean;
}

export const ProblemDetailsPanel: FC<ProblemDetailsPanelProps> = ({
  problem,
  onResetStarterCode,
  onSubmit,
  isSubmitting,
}) => {
  const [showHint, setShowHint] = useState(false);

  const getDifficultyBadge = (diff: string) => {
    switch (diff) {
      case 'EASY':
        return <span className="badge-success text-[10px] font-bold">Easy</span>;
      case 'MEDIUM':
        return <span className="badge-warning text-[10px] font-bold">Medium</span>;
      case 'HARD':
        return <span className="badge-danger text-[10px] font-bold">Hard</span>;
      default:
        return <span className="badge-brand text-[10px] font-bold">{diff}</span>;
    }
  };

  return (
    <div className="card p-5 sm:p-6 space-y-5 text-slate-900">
      {/* ── Problem Header ── */}
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            {problem.course_code && (
              <span className="badge-brand font-mono font-bold text-[10px]">
                {problem.course_code} · Unit {problem.unit_number || '1'}
              </span>
            )}
            {getDifficultyBadge(problem.difficulty)}
          </div>
          {problem.is_solved && (
            <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
              <CheckCircle2 size={13} /> Solved
            </span>
          )}
        </div>

        <h2 className="text-lg sm:text-xl font-bold text-slate-900 font-heading leading-tight">
          {problem.title}
        </h2>
        {problem.topic_name && (
          <p className="text-xs text-slate-500">
            Syllabus topic: <strong className="text-slate-800">{problem.topic_name}</strong>
          </p>
        )}
      </div>

      {/* ── Problem Description ── */}
      <div className="text-xs sm:text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
        {problem.description}
      </div>

      {/* ── Examples & Sample I/O ── */}
      {problem.examples && (
        <div className="space-y-1.5">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Sample Examples &amp; Constraints
          </div>
          <pre className="p-3 bg-slate-50 border border-slate-200 text-slate-800 rounded-lg font-mono text-xs overflow-x-auto whitespace-pre-wrap">
            {problem.examples}
          </pre>
        </div>
      )}

      {/* ── Public Test Cases Preview ── */}
      {problem.public_test_cases && problem.public_test_cases.length > 0 && (
        <div className="space-y-2">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Public Test Cases ({problem.public_test_cases.length})
          </div>
          <div className="space-y-1.5">
            {problem.public_test_cases.map(tc => (
              <div key={tc.test_index} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs font-mono">
                <div className="text-[10px] font-bold text-slate-500 mb-1">Test Case {tc.test_index}</div>
                {tc.input_text && <div><span className="text-slate-500">Input:</span> <span className="text-slate-900">{tc.input_text}</span></div>}
                <div><span className="text-slate-500">Expected:</span> <span className="text-slate-900">{tc.expected_output}</span></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Hints Accordion ── */}
      {problem.hints && (
        <div className="border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
          <button
            onClick={() => setShowHint(h => !h)}
            className="w-full flex items-center justify-between p-3 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <div className="flex items-center gap-1.5">
              <HelpCircle size={14} className="text-blue-600" />
              <span>Problem Hint</span>
            </div>
            {showHint ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showHint && (
            <div className="p-3 text-xs text-slate-600 bg-white border-t border-slate-200 leading-relaxed">
              {problem.hints}
            </div>
          )}
        </div>
      )}

      {/* ── Bottom Challenge Actions ── */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-3">
        <button
          onClick={onResetStarterCode}
          className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
          title="Reset code template"
        >
          <RotateCcw size={12} />
          <span>Reset Code</span>
        </button>

        <button
          onClick={onSubmit}
          disabled={isSubmitting}
          className="btn-primary text-xs py-2 px-4 shadow-sm"
        >
          {isSubmitting ? 'Evaluating Test Cases…' : 'Submit Challenge'}
        </button>
      </div>
    </div>
  );
};
