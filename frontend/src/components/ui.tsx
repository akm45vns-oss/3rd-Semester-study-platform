import { type FC, type ReactNode } from 'react';
import { clsx } from 'clsx';
import { Check, CloudOff, RefreshCw, AlertCircle, AlertOctagon } from 'lucide-react';
import type { TopicStatus, PracticalStatus } from '../types';

// ── Progress Bar ────────────────────────────────────────────────────────
interface ProgressBarProps {
  value: number; // 0-100
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
}

const sizeMap = {
  sm: 'h-1.5',
  md: 'h-2',
  lg: 'h-2.5',
};

export const ProgressBar: FC<ProgressBarProps> = ({
  value, className, size = 'md', showLabel = false, label,
}) => {
  const pct = Math.min(100, Math.max(0, value));

  return (
    <div className={clsx('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1 text-xs">
          {label && <span className="font-medium text-slate-500">{label}</span>}
          {showLabel && <span className="font-mono font-semibold text-slate-900">{pct.toFixed(0)}%</span>}
        </div>
      )}
      <div className={clsx('w-full bg-slate-200 rounded-full overflow-hidden', sizeMap[size])}>
        <div
          className="h-full bg-slate-900 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
};

// ── Status Badge ────────────────────────────────────────────────────────
const statusConfig: Record<TopicStatus | PracticalStatus, { label: string; icon: string; className: string }> = {
  NOT_STARTED:    { label: 'Not Started',    icon: '○', className: 'text-slate-500' },
  LEARNING:       { label: 'In Progress',    icon: '◐', className: 'text-blue-600 font-semibold' },
  LEARNED:        { label: 'Mastered',       icon: '✓', className: 'text-emerald-700 font-semibold' },
  NEEDS_REVISION: { label: 'Needs Revision', icon: '↻', className: 'text-amber-700 font-semibold' },
  IN_PROGRESS:    { label: 'In Progress',    icon: '◐', className: 'text-blue-600 font-semibold' },
  COMPLETED:      { label: 'Completed',      icon: '✓', className: 'text-emerald-700 font-semibold' },
  NEEDS_REDO:     { label: 'Needs Redo',     icon: '↻', className: 'text-amber-700 font-semibold' },
};

export const StatusBadge: FC<{ status: TopicStatus | PracticalStatus; className?: string }> = ({ status, className }) => {
  const cfg = statusConfig[status] ?? { label: status, icon: '·', className: 'text-slate-500' };
  return (
    <span className={clsx('inline-flex items-center gap-1 text-[11px]', cfg.className, className)}>
      <span className="font-mono text-[10px]">{cfg.icon}</span>
      <span>{cfg.label}</span>
    </span>
  );
};

// ── Save Status ─────────────────────────────────────────────────────────
export type SaveState = 'SAVED' | 'SAVING' | 'OFFLINE' | 'SYNCING' | 'ERROR';

export const SaveStatus: FC<{ state: SaveState; className?: string }> = ({ state, className }) => {
  if (state === 'SAVED') {
    return (
      <span className={clsx('inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700', className)}>
        <Check size={12} className="text-emerald-600" />
        <span>Saved</span>
      </span>
    );
  }
  if (state === 'SAVING') {
    return (
      <span className={clsx('inline-flex items-center gap-1 text-[11px] font-medium text-slate-500', className)}>
        <RefreshCw size={11} className="animate-spin text-slate-400" />
        <span>Saving…</span>
      </span>
    );
  }
  if (state === 'OFFLINE') {
    return (
      <span className={clsx('inline-flex items-center gap-1 text-[11px] font-medium text-slate-500', className)}>
        <CloudOff size={11} className="text-slate-400" />
        <span>Saved locally</span>
      </span>
    );
  }
  if (state === 'SYNCING') {
    return (
      <span className={clsx('inline-flex items-center gap-1 text-[11px] font-medium text-blue-600', className)}>
        <RefreshCw size={11} className="animate-spin text-blue-600" />
        <span>Syncing…</span>
      </span>
    );
  }
  return null;
};

// ── Spinner ─────────────────────────────────────────────────────────────
export const Spinner: FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ size = 'md', className }) => {
  const sMap = { sm: 'w-3.5 h-3.5', md: 'w-5 h-5', lg: 'w-7 h-7' };
  return (
    <div
      className={clsx('animate-spin rounded-full border-2 border-slate-200 border-t-slate-900 shrink-0', sMap[size], className)}
      role="status"
      aria-label="loading"
    />
  );
};

// ── Error Alert ─────────────────────────────────────────────────────────
export const ErrorAlert: FC<{ message: string; onRetry?: () => void; className?: string }> = ({
  message, onRetry, className,
}) => (
  <div className={clsx('p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-2.5', className)}>
    <AlertCircle size={15} className="text-red-600 shrink-0 mt-0.5" />
    <div className="flex-1">
      <div className="font-semibold text-red-900">Notice</div>
      <div className="text-red-700 mt-0.5 leading-relaxed">{message}</div>
    </div>
    {onRetry && (
      <button onClick={onRetry} className="btn-secondary text-[11px] py-1 px-2.5 shrink-0 bg-white">
        Retry
      </button>
    )}
  </div>
);

// ── Empty State ─────────────────────────────────────────────────────────
export const EmptyState: FC<{
  icon?: FC<{ size?: number; className?: string }>;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}> = ({ icon: Icon = AlertOctagon, title, description, action, className }) => (
  <div className={clsx('text-center py-10 px-4 space-y-3 max-w-sm mx-auto', className)}>
    <div className="w-10 h-10 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
      <Icon size={20} />
    </div>
    <div>
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      {description && <p className="text-xs text-slate-500 mt-1 leading-relaxed">{description}</p>}
    </div>
    {action && <div className="pt-2">{action}</div>}
  </div>
);
