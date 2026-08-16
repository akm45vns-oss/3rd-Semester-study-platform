import { type FC, useState, useRef } from 'react';
import { Copy, Check, RotateCcw, Trash2, Code2, Play } from 'lucide-react';

interface CodeEditorProps {
  code: string;
  onChange: (newCode: string) => void;
  language: string;
  fileName: string;
  onRun: () => void;
  onReset: () => void;
  isExecuting: boolean;
  disabled?: boolean;
}

export const CodeEditor: FC<CodeEditorProps> = ({
  code,
  onChange,
  language,
  fileName,
  onRun,
  onReset,
  isExecuting,
  disabled = false,
}) => {
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const lines = code.split('\n');
  const lineCount = Math.max(lines.length, 16);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onRun();
      return;
    }

    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;

      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      onChange(newCode);

      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
        }
      }, 0);
    }
  };

  return (
    <div className="flex flex-col bg-slate-950 text-slate-100 rounded-xl border border-slate-800 shadow-sm overflow-hidden w-full transition-all">
      {/* ── Editor Header Toolbar ── */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <Code2 size={14} className="text-blue-400" />
          <span className="font-mono font-semibold text-slate-200 text-xs">{fileName}</span>
          <span className="text-[10px] font-mono font-semibold bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
            {language}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={onReset}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
            title="Reset to official starter template"
          >
            <RotateCcw size={13} />
          </button>

          <button
            onClick={() => onChange('')}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
            title="Clear code"
          >
            <Trash2 size={13} />
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-0.5 bg-slate-800 hover:bg-slate-700 rounded text-xs font-mono text-slate-300 transition-colors"
            title="Copy code"
          >
            {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={onRun}
            disabled={isExecuting || disabled}
            className="btn-accent text-xs py-1 px-3 flex items-center gap-1.5 shadow-sm"
          >
            <Play size={12} className="fill-white" />
            <span>{isExecuting ? 'Running…' : 'Run'}</span>
          </button>
        </div>
      </div>

      {/* ── Code Editor Body ── */}
      <div className="relative flex flex-1 min-h-[320px] font-mono text-xs leading-6 overflow-hidden bg-slate-950">
        {/* Line Numbers */}
        <div className="select-none py-3 px-3 bg-slate-900/40 text-slate-600 text-right border-r border-slate-800 font-mono text-xs w-12 shrink-0">
          {Array.from({ length: lineCount }).map((_, i) => (
            <div key={i} className="leading-6">{i + 1}</div>
          ))}
        </div>

        {/* Textarea Code Input */}
        <div className="relative flex-1 h-full min-w-0">
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="// Write code here..."
            spellCheck={false}
            autoCapitalize="off"
            autoComplete="off"
            autoCorrect="off"
            className="w-full h-full min-h-[320px] py-3 px-3.5 bg-transparent text-slate-100 font-mono leading-6 resize-none outline-none border-none whitespace-pre tab-4 text-xs sm:text-sm"
          />
        </div>
      </div>
    </div>
  );
};
