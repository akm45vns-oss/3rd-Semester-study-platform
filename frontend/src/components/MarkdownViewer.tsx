import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Copy, Check, BookOpen, Terminal
} from 'lucide-react';

interface MarkdownViewerProps {
  content: string;
  className?: string;
  topicTitle?: string;
}

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-lg overflow-hidden border border-slate-800 bg-slate-950 text-slate-100 shadow-sm">
      <div className="flex items-center justify-between px-3.5 py-2 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-1.5">
          <Terminal size={12} className="text-blue-400" />
          <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-300">
            {language || 'code'}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-0.5 text-[11px] text-slate-300 hover:text-white
                     bg-slate-800 hover:bg-slate-700 rounded font-mono transition-colors"
          title="Copy code block"
        >
          {copied ? (
            <>
              <Check size={11} className="text-emerald-400" />
              <span className="text-emerald-400 font-bold">Copied</span>
            </>
          ) : (
            <>
              <Copy size={11} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <div className="p-4 overflow-x-auto text-xs font-mono text-slate-100 leading-relaxed bg-slate-950">
        <pre className="!m-0 !p-0">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
}

export function MarkdownViewer({ content, className = '', topicTitle }: MarkdownViewerProps) {
  const [copiedAll, setCopiedAll] = useState(false);

  const handleCopyAll = () => {
    navigator.clipboard.writeText(content);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  return (
    <div className={`max-w-3xl mx-auto ${className}`}>
      {/* Top Academic Metadata Bar */}
      <div className="flex items-center justify-between pb-3 mb-6 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <BookOpen size={15} className="text-blue-600" />
          <span className="text-xs font-semibold text-slate-700">
            {topicTitle ? `${topicTitle} • Academic Theory Notes` : 'Syllabus Theory Notes'}
          </span>
        </div>
        <button
          onClick={handleCopyAll}
          className="btn-secondary text-[11px] py-1 px-2.5 flex items-center gap-1.5"
        >
          {copiedAll ? <Check size={12} className="text-emerald-600" /> : <Copy size={12} />}
          <span>{copiedAll ? 'Notes Copied' : 'Copy All'}</span>
        </button>
      </div>

      {/* Markdown Content */}
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 font-heading mt-6 mb-3 pb-2 border-b border-slate-200">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-bold text-slate-900 font-heading mt-6 mb-2">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold text-slate-900 mt-4 mb-2">
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className="text-sm text-slate-700 leading-relaxed mb-4">
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-1.5 text-sm text-slate-700 mb-4 pl-2">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside space-y-1.5 text-sm text-slate-700 mb-4 pl-2">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-sm text-slate-700 leading-relaxed">
              {children}
            </li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-slate-300 pl-4 py-1 my-4 bg-slate-50 rounded-r-lg text-sm text-slate-700 italic">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-5 rounded-lg border border-slate-200">
              <table className="w-full text-xs text-left text-slate-800">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-slate-100 text-slate-900 font-semibold border-b border-slate-200">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-slate-200 bg-white">
              {children}
            </tbody>
          ),
          th: ({ children }) => (
            <th className="px-3.5 py-2.5 font-semibold">{children}</th>
          ),
          td: ({ children }) => (
            <td className="px-3.5 py-2">{children}</td>
          ),
          code: ({ className: codeClassName, children, ...props }) => {
            const match = /language-(\w+)/.exec(codeClassName || '');
            const isInline = !match && !String(children).includes('\n');

            if (isInline) {
              return (
                <code
                  className="px-1.5 py-0.5 text-xs font-mono bg-slate-100 text-slate-900 border border-slate-200 rounded"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <CodeBlock
                language={match ? match[1] : ''}
                code={String(children).replace(/\n$/, '')}
              />
            );
          },
          hr: () => <hr className="my-6 border-slate-200" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
