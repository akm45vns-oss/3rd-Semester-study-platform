import { type FC, useEffect, useState } from 'react';
import {
  Play, Pause, Square, Award,
  Clock,
} from 'lucide-react';
import { useStudySessionStore } from '../stores/studySessionStore';

export const StudySessionBar: FC = () => {
  const { activeSession, elapsedSeconds, isPaused, tick, pauseSession, resumeSession, finishSession } = useStudySessionStore();
  const [finishing, setFinishing] = useState(false);

  useEffect(() => {
    if (!activeSession) return;
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [activeSession, tick]);

  if (!activeSession) return null;

  const formatTime = (secs: number) => {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    if (h > 0) {
      return `${h}:${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
    }
    return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleFinish = async () => {
    setFinishing(true);
    try {
      await finishSession();
    } finally {
      setFinishing(false);
    }
  };

  return (
    <div className="fixed bottom-16 md:bottom-5 right-5 z-40 animate-fade-in">
      <div className="flex items-center gap-3 px-3.5 py-2 bg-slate-900 text-white rounded-xl shadow-lg border border-slate-700">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <Clock size={15} className="text-slate-400" />
          <span className="font-mono font-bold text-xs tracking-wider text-white">
            {formatTime(elapsedSeconds)}
          </span>
        </div>

        <div className="h-4 w-px bg-slate-700" />

        <div className="flex items-center gap-1">
          {isPaused ? (
            <button
              onClick={resumeSession}
              className="p-1 hover:bg-slate-800 rounded transition-colors text-slate-300 hover:text-white"
              title="Resume session"
            >
              <Play size={14} />
            </button>
          ) : (
            <button
              onClick={pauseSession}
              className="p-1 hover:bg-slate-800 rounded transition-colors text-slate-300 hover:text-white"
              title="Pause session"
            >
              <Pause size={14} />
            </button>
          )}

          <button
            onClick={handleFinish}
            disabled={finishing}
            className="flex items-center gap-1 px-2 py-0.5 bg-white text-slate-900 hover:bg-slate-100 rounded-md text-xs font-semibold transition-all shadow-sm ml-1"
          >
            <Square size={11} className="fill-slate-900" />
            <span>Finish</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export const StudySessionModal: FC = () => {
  const { completedSummary, clearCompletedSummary } = useStudySessionStore();

  if (!completedSummary) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={clearCompletedSummary} />

      <div className="relative z-10 w-full max-w-md bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-xl animate-fade-in text-slate-900 text-center space-y-5">
        <div className="w-14 h-14 bg-slate-100 text-slate-900 rounded-xl flex items-center justify-center mx-auto shadow-sm border border-slate-200">
          <Award size={28} />
        </div>

        <div className="space-y-1">
          <h3 className="text-xl font-bold font-heading text-slate-900">Study Session Complete</h3>
          <p className="text-xs text-slate-500">
            Great progress! Your session statistics have been saved.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <div>
            <div className="text-2xl font-bold font-mono text-slate-900">
              {completedSummary.durationMinutes}m
            </div>
            <div className="text-[11px] font-semibold text-slate-500">Time Studied</div>
          </div>
          <div>
            <div className="text-2xl font-bold font-mono text-slate-900">
              {completedSummary.topicsStudied || 1}
            </div>
            <div className="text-[11px] font-semibold text-slate-500">Topics Covered</div>
          </div>
        </div>

        <div className="pt-2 flex gap-2">
          <button
            onClick={clearCompletedSummary}
            className="btn-primary w-full text-xs py-2.5 font-semibold justify-center"
          >
            Continue Studying
          </button>
        </div>
      </div>
    </div>
  );
};
