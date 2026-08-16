import { type FC, useState, useRef, useEffect } from 'react';
import {
  Terminal, CheckCircle2, XCircle, Clock, AlertTriangle,
  CornerDownLeft, Trash2,
} from 'lucide-react';
import type { CodeExecuteResult, PracticeSubmitResult, PublicTestCase } from '../../types';

interface OutputPanelProps {
  execResult: CodeExecuteResult | null;
  submitResult: PracticeSubmitResult | null;
  isExecuting: boolean;
  onClear: () => void;
  stdinInput: string;
  onStdinChange: (val: string) => void;
  onRun: () => void;
  supportsStdin: boolean;
  languageName: string;
}

export const OutputPanel: FC<OutputPanelProps> = ({
  execResult,
  submitResult,
  isExecuting,
  onClear,
  stdinInput,
  onStdinChange,
  onRun,
  supportsStdin,
  languageName,
}) => {
  const [activeInput, setActiveInput] = useState(stdinInput);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setActiveInput(stdinInput);
  }, [stdinInput]);

  const handleSendInput = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    onStdinChange(activeInput);
    onRun();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSendInput();
    }
  };

  const res = submitResult || execResult;
  const status = res?.status;

  const getStatusBadge = () => {
    if (!status) {
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] font-mono font-medium">
          <Terminal size={12} className="text-blue-400" />
          <span>Interactive Terminal</span>
        </span>
      );
    }
    switch (status) {
      case 'ACCEPTED':
      case 'PASSED':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 bg-emerald-900/60 text-emerald-300 border border-emerald-700 rounded text-[11px] font-mono font-semibold">
            <CheckCircle2 size={12} />
            <span>Accepted</span>
          </span>
        );
      case 'WRONG_ANSWER':
      case 'FAILED':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 bg-rose-900/60 text-rose-300 border border-rose-700 rounded text-[11px] font-mono font-semibold">
            <XCircle size={12} />
            <span>Wrong Answer</span>
          </span>
        );
      case 'COMPILATION_ERROR':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 bg-rose-900/60 text-rose-300 border border-rose-700 rounded text-[11px] font-mono font-semibold">
            <AlertTriangle size={12} />
            <span>Compilation Error</span>
          </span>
        );
      case 'TIME_LIMIT_EXCEEDED':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-900/60 text-amber-300 border border-amber-700 rounded text-[11px] font-mono font-semibold">
            <Clock size={12} />
            <span>Time Limit Exceeded</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] font-mono font-semibold">
            <Terminal size={12} />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col bg-slate-950 text-slate-100 rounded-xl border border-slate-800 shadow-sm overflow-hidden w-full transition-all">
      {/* ── Terminal Header ── */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          {getStatusBadge()}
          {res?.execution_time_ms !== undefined && res.execution_time_ms > 0 && (
            <span className="text-[10px] font-mono text-slate-400">
              {res.execution_time_ms} ms
            </span>
          )}
        </div>

        <button
          onClick={onClear}
          className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
          title="Clear terminal output"
        >
          <Trash2 size={13} />
        </button>
      </div>

      {/* ── Terminal Display Area ── */}
      <div className="p-4 font-mono text-xs leading-relaxed min-h-[140px] max-h-[320px] overflow-y-auto space-y-2 bg-slate-950">
        {isExecuting ? (
          <div className="flex items-center gap-2 text-slate-400">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
            <span>Executing program on secure runtime sandbox…</span>
          </div>
        ) : !res ? (
          <div className="text-slate-500 py-6 text-center space-y-1">
            <div>Click "Run" or press Ctrl + Enter to execute code.</div>
            {supportsStdin && (
              <div className="text-[11px] text-slate-600">
                You can provide input interactively using the prompt bar below.
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Output message / Stdout */}
            {(execResult?.stdout || submitResult?.output_message) && (
              <div className="text-slate-100 whitespace-pre-wrap selection:bg-slate-800">
                {execResult?.stdout || submitResult?.output_message}
              </div>
            )}

            {/* Compilation or Runtime Error */}
            {(execResult?.compile_error || execResult?.runtime_error || execResult?.stderr || submitResult?.compile_error || submitResult?.runtime_error) && (
              <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 whitespace-pre-wrap">
                {execResult?.compile_error || execResult?.runtime_error || execResult?.stderr || submitResult?.compile_error || submitResult?.runtime_error}
              </div>
            )}

            {/* Challenge Test Cases Results */}
            {submitResult && submitResult.public_test_results && (
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <div className="text-[11px] font-bold text-slate-400">Test Cases Passed:</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {submitResult.public_test_results.map((tc: PublicTestCase, i: number) => (
                    <div
                      key={i}
                      className={`p-2.5 rounded border text-[11px] space-y-1 ${
                        tc.passed
                          ? 'bg-emerald-950/30 border-emerald-800 text-emerald-300'
                          : 'bg-rose-950/30 border-rose-800 text-rose-300'
                      }`}
                    >
                      <div className="flex items-center justify-between font-bold">
                        <span>Case #{i + 1}</span>
                        <span>{tc.passed ? '✓ Passed' : '✗ Failed'}</span>
                      </div>
                      <div className="text-slate-400 truncate">Input: {tc.input_text || '(None)'}</div>
                      <div className="text-slate-400 truncate">Expected: {tc.expected_output}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Interactive Input Prompt (Integrated Terminal Line) ── */}
      {supportsStdin && (
        <form onSubmit={handleSendInput} className="flex items-center gap-2 px-3 py-2 bg-slate-900 border-t border-slate-800">
          <span className="font-mono text-xs font-bold text-blue-400 select-none pl-1">stdin &gt;</span>
          <input
            ref={inputRef}
            type="text"
            value={activeInput}
            onChange={(e) => setActiveInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Enter input for ${languageName} program (e.g. numbers, words)...`}
            className="flex-1 bg-transparent border-none text-xs font-mono text-slate-100 placeholder-slate-500 outline-none"
          />
          <button
            type="submit"
            disabled={isExecuting}
            className="btn-accent text-[11px] py-1 px-2.5 flex items-center gap-1 shadow-sm"
          >
            <span>Send &amp; Run</span>
            <CornerDownLeft size={11} />
          </button>
        </form>
      )}
    </div>
  );
};
