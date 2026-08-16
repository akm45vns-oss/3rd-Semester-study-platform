import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Terminal, BookOpen, Search, ArrowLeft, ArrowRight,
  Code2,
} from 'lucide-react';
import { codingApi } from '../api';
import { extractErrorMessage } from '../api/client';
import type { CodingProblem, CodeExecuteResult, PracticeSubmitResult } from '../types';
import { AppLayout, Breadcrumb } from '../components/layout';
import { CodeEditor } from '../components/lab/CodeEditor';
import { OutputPanel } from '../components/lab/OutputPanel';
import { ProblemDetailsPanel } from '../components/lab/ProblemDetailsPanel';
import { CLIENT_LANGUAGES, getClientLanguage, type ClientLanguageConfig } from '../components/lab/languageRegistry';
import { useAuthStore } from '../stores/authStore';
import { useStudySessionStore } from '../stores/studySessionStore';

export default function CodingLabPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuthStore();
  const { incrementTopicCount } = useStudySessionStore();

  const [labMode, setLabMode] = useState<'FREE' | 'PRACTICE'>('FREE');
  const [selectedLanguage, setSelectedLanguage] = useState<ClientLanguageConfig>(CLIENT_LANGUAGES[0]);
  const [code, setCode] = useState<string>(selectedLanguage.starterCode);
  const [stdinInput, setStdinInput] = useState<string>(selectedLanguage.sampleStdin);

  // Practice Problems State
  const [problems, setProblems] = useState<CodingProblem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<CodingProblem | null>(null);
  const [practiceSearch, setPracticeSearch] = useState('');
  const [practiceLanguageFilter, setPracticeLanguageFilter] = useState('ALL');
  const [practiceDiffFilter, setPracticeDiffFilter] = useState('ALL');

  // Execution & Diagnostics States
  const [isExecuting, setIsExecuting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [execResult, setExecResult] = useState<CodeExecuteResult | null>(null);
  const [submitResult, setSubmitResult] = useState<PracticeSubmitResult | null>(null);

  const getDraftKey = useCallback((langId: string) => {
    const uId = user?.id || 'default';
    return `semester_os_lab_draft:${uId}:${langId}`;
  }, [user?.id]);

  const loadLanguageCode = useCallback((langConfig: ClientLanguageConfig) => {
    const saved = localStorage.getItem(getDraftKey(langConfig.id));
    if (saved && saved.trim()) {
      setCode(saved);
    } else {
      setCode(langConfig.starterCode);
    }
    setStdinInput(langConfig.sampleStdin);
  }, [getDraftKey]);

  useEffect(() => {
    const initMode = searchParams.get('mode');
    const initProbId = searchParams.get('problem_id');
    const initLang = searchParams.get('language') || searchParams.get('subject_id');

    if (initProbId || initMode === 'practice') {
      setLabMode('PRACTICE');
    } else {
      setLabMode('FREE');
    }

    codingApi.getProblems().then(setProblems).catch(console.error);

    if (initLang) {
      const match = CLIENT_LANGUAGES.find(l =>
        l.id.toLowerCase() === initLang.toLowerCase() ||
        l.courseCode.toLowerCase() === initLang.toLowerCase()
      );
      if (match) {
        setSelectedLanguage(match);
        loadLanguageCode(match);
      }
    } else {
      loadLanguageCode(selectedLanguage);
    }
  }, []);

  useEffect(() => {
    const probId = searchParams.get('problem_id');
    if (probId && problems.length > 0) {
      const found = problems.find(p => p.id === Number(probId));
      if (found) {
        handleSelectPracticeProblem(found);
      }
    }
  }, [problems, searchParams]);

  const handleLanguageChange = (langId: string) => {
    try {
      localStorage.setItem(getDraftKey(selectedLanguage.id), code);
    } catch {}

    const newLang = getClientLanguage(langId);
    setSelectedLanguage(newLang);
    loadLanguageCode(newLang);
    setExecResult(null);
  };

  const handleRunFreeCode = async () => {
    if (isExecuting) return;
    setIsExecuting(true);
    try {
      if (selectedLanguage.id === 'SQL') {
        const res = await codingApi.executeSql(code);
        setExecResult({
          status: 'ACCEPTED',
          stdout: res.columns && res.columns.length > 0
            ? `${res.columns.join(' | ')}\n${'-'.repeat(40)}\n` +
              res.rows.map(r => res.columns.map(c => r[c]).join(' | ')).join('\n') +
              `\n\n(${res.row_count} rows returned)`
            : `Query executed successfully (${res.row_count} rows affected)`,
          stderr: '',
          execution_time_ms: 0,
          memory_usage_mb: 0,
          exit_code: 0,
        });
      } else {
        const res = await codingApi.executeCode({
          language: selectedLanguage.id,
          source_code: code,
          stdin: stdinInput,
        });
        setExecResult(res);
      }
    } catch (err) {
      console.error(err);
      setExecResult({
        status: 'RUNTIME_ERROR',
        stdout: '',
        stderr: extractErrorMessage(err, 'Failed to execute code.'),
        execution_time_ms: 0,
        memory_usage_mb: 0,
        exit_code: 1,
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleResetCode = () => {
    if (window.confirm('Reset code to starter template?')) {
      setCode(selectedLanguage.starterCode);
      setStdinInput(selectedLanguage.sampleStdin);
      localStorage.removeItem(getDraftKey(selectedLanguage.id));
    }
  };

  const handleSelectPracticeProblem = (prob: CodingProblem) => {
    setSelectedProblem(prob);
    const lang = getClientLanguage(prob.language || 'PYTHON');
    setSelectedLanguage(lang);

    const draftKey = `semester_os_problem_draft:${user?.id || 'default'}:${prob.id}`;
    const saved = localStorage.getItem(draftKey);
    setCode(saved && saved.trim() ? saved : prob.starter_code || lang.starterCode);
    setStdinInput('');
    setExecResult(null);
    setSubmitResult(null);
  };

  const handleSubmitProblem = async () => {
    if (!selectedProblem || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const res = await codingApi.submitCode({
        problem_id: selectedProblem.id,
        code: code,
        language: selectedProblem.language || selectedLanguage.id,
      });
      setSubmitResult(res);

      if (res.passed) {
        setProblems(prev =>
          prev.map(p => p.id === selectedProblem.id ? { ...p, is_solved: true } : p)
        );
        setSelectedProblem(prev => prev ? { ...prev, is_solved: true } : null);
        incrementTopicCount();
      }
    } catch (err) {
      console.error(err);
      alert(extractErrorMessage(err, 'Failed to submit problem.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSwitchToFree = () => {
    setLabMode('FREE');
    setSelectedProblem(null);
    setSearchParams({});
    loadLanguageCode(selectedLanguage);
  };

  const handleSwitchToPractice = () => {
    setLabMode('PRACTICE');
    setSearchParams({ mode: 'practice' });
  };

  const filteredProblems = problems.filter(p => {
    if (practiceLanguageFilter !== 'ALL' && p.language?.toUpperCase() !== practiceLanguageFilter) {
      return false;
    }
    if (practiceDiffFilter !== 'ALL' && p.difficulty !== practiceDiffFilter) {
      return false;
    }
    if (practiceSearch.trim()) {
      const q = practiceSearch.toLowerCase();
      const matchTitle = p.title.toLowerCase().includes(q);
      const matchTopic = (p.topic_name || '').toLowerCase().includes(q);
      const matchCode = (p.course_code || '').toLowerCase().includes(q);
      if (!matchTitle && !matchTopic && !matchCode) return false;
    }
    return true;
  });

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto space-y-5 animate-fade-in text-slate-900 pb-16">
        {/* ── Top Header & Mode Switcher ── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
          <Breadcrumb items={[
            { label: 'Home', to: '/dashboard' },
            { label: 'Coding Lab', to: '/coding' },
            { label: labMode === 'FREE' ? 'Compiler' : (selectedProblem ? selectedProblem.title : 'Challenges') },
          ]} />

          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 shrink-0">
            <button
              onClick={handleSwitchToFree}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${
                labMode === 'FREE'
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Terminal size={13} />
              <span>Compiler</span>
            </button>

            <button
              onClick={handleSwitchToPractice}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${
                labMode === 'PRACTICE'
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <BookOpen size={13} />
              <span>Challenges ({problems.length})</span>
            </button>
          </div>
        </div>

        {/* ── MODE 1: FREE COMPILER ── */}
        {labMode === 'FREE' && (
          <div className="space-y-4">
            {/* Language Switcher Toolbar */}
            <div className="flex items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 flex-wrap">
              <div className="flex items-center gap-2">
                <Code2 size={15} className="text-blue-600" />
                <span className="text-xs font-semibold text-slate-700">Language:</span>
                <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
                  {CLIENT_LANGUAGES.map(lang => (
                    <button
                      key={lang.id}
                      onClick={() => handleLanguageChange(lang.id)}
                      className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                        selectedLanguage.id === lang.id
                          ? 'bg-white text-slate-900 shadow-sm border border-slate-200 font-semibold'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="text-xs text-slate-500 hidden md:block">
                {selectedLanguage.badge} · Preloaded libraries ready
              </div>
            </div>

            {/* Editor & Unified Terminal Output */}
            <div className="space-y-4">
              <CodeEditor
                code={code}
                onChange={setCode}
                language={selectedLanguage.name}
                fileName={selectedLanguage.fileName}
                onRun={handleRunFreeCode}
                onReset={handleResetCode}
                isExecuting={isExecuting}
              />

              <OutputPanel
                execResult={execResult}
                submitResult={null}
                isExecuting={isExecuting}
                onClear={() => setExecResult(null)}
                stdinInput={stdinInput}
                onStdinChange={setStdinInput}
                onRun={handleRunFreeCode}
                supportsStdin={selectedLanguage.supportsStdin}
                languageName={selectedLanguage.name}
              />
            </div>
          </div>
        )}

        {/* ── MODE 2: PRACTICE CHALLENGES ── */}
        {labMode === 'PRACTICE' && (
          <div>
            {!selectedProblem ? (
              <div className="space-y-4">
                {/* Search & Filter Header */}
                <div className="card p-4 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="relative flex-1">
                      <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={practiceSearch}
                        onChange={(e) => setPracticeSearch(e.target.value)}
                        placeholder="Search challenges by title or topic..."
                        className="input pl-8 text-xs font-medium py-2"
                      />
                    </div>

                    {/* Language Filter */}
                    <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
                      {['ALL', 'JAVA', 'PYTHON', 'JAVASCRIPT', 'SQL'].map(lang => (
                        <button
                          key={lang}
                          onClick={() => setPracticeLanguageFilter(lang)}
                          className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                            practiceLanguageFilter === lang
                              ? 'bg-white text-slate-900 shadow-sm border border-slate-200 font-semibold'
                              : 'text-slate-600 hover:text-slate-900'
                          }`}
                        >
                          {lang === 'ALL' ? 'All' : lang}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Difficulty Filter */}
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 text-xs font-medium text-slate-500">
                    <span>Difficulty:</span>
                    {['ALL', 'EASY', 'MEDIUM', 'HARD'].map(diff => (
                      <button
                        key={diff}
                        onClick={() => setPracticeDiffFilter(diff)}
                        className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                          practiceDiffFilter === diff
                            ? 'bg-slate-900 text-white'
                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                        }`}
                      >
                        {diff}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Challenge Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {filteredProblems.map(prob => (
                    <div
                      key={prob.id}
                      onClick={() => handleSelectPracticeProblem(prob)}
                      className="card p-4 hover:border-slate-300 cursor-pointer transition-all space-y-2.5 flex flex-col justify-between"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between gap-2">
                          <span className="badge-brand font-mono text-[10px] font-bold">
                            {prob.course_code} · Unit {prob.unit_number || '1'}
                          </span>
                          <span className={`text-[10px] font-bold ${
                            prob.difficulty === 'EASY' ? 'text-emerald-700' : prob.difficulty === 'MEDIUM' ? 'text-amber-700' : 'text-rose-700'
                          }`}>
                            {prob.difficulty}
                          </span>
                        </div>

                        <h3 className="text-sm font-bold text-slate-900 line-clamp-1">
                          {prob.title}
                        </h3>

                        {prob.topic_name && (
                          <p className="text-xs text-slate-500 line-clamp-1">{prob.topic_name}</p>
                        )}
                      </div>

                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                        <span className="font-mono text-[11px] text-slate-500 font-semibold">{prob.language}</span>
                        <span className="text-blue-600 font-semibold flex items-center gap-1">
                          <span>Solve</span>
                          <ArrowRight size={12} />
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              /* Problem Solving View: 2-Column Split Desktop / Stacked Mobile */
              <div className="space-y-4">
                <button
                  onClick={() => setSelectedProblem(null)}
                  className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
                >
                  <ArrowLeft size={13} />
                  <span>Back to Challenge List</span>
                </button>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
                  {/* Left Column: Problem Details Panel (Col 5) */}
                  <div className="lg:col-span-5 space-y-4">
                    <ProblemDetailsPanel
                      problem={selectedProblem}
                      onResetStarterCode={() => setCode(selectedProblem.starter_code || '')}
                      onSubmit={handleSubmitProblem}
                      isSubmitting={isSubmitting}
                    />
                  </div>

                  {/* Right Column: Code Editor + Output Panel (Col 7) */}
                  <div className="lg:col-span-7 space-y-4">
                    <CodeEditor
                      code={code}
                      onChange={setCode}
                      language={selectedLanguage.name}
                      fileName={selectedLanguage.fileName}
                      onRun={handleRunFreeCode}
                      onReset={() => setCode(selectedProblem.starter_code || '')}
                      isExecuting={isExecuting}
                    />

                    <OutputPanel
                      execResult={execResult}
                      submitResult={submitResult}
                      isExecuting={isExecuting || isSubmitting}
                      onClear={() => { setExecResult(null); setSubmitResult(null); }}
                      stdinInput={stdinInput}
                      onStdinChange={setStdinInput}
                      onRun={handleRunFreeCode}
                      supportsStdin={selectedLanguage.supportsStdin}
                      languageName={selectedLanguage.name}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
