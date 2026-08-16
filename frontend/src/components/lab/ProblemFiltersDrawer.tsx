import { type FC, useState } from 'react';
import { Search, Filter, CheckCircle2, Circle, ChevronRight } from 'lucide-react';
import type { CodingProblem } from '../../types';

interface ProblemFiltersDrawerProps {
  problems: CodingProblem[];
  selectedProblemId: number | null;
  onSelectProblem: (problem: CodingProblem) => void;
  languageFilter: string;
  onLanguageFilterChange: (lang: string) => void;
}

export const ProblemFiltersDrawer: FC<ProblemFiltersDrawerProps> = ({
  problems,
  selectedProblemId,
  onSelectProblem,
  languageFilter,
  onLanguageFilterChange,
}) => {
  const [search, setSearch] = useState('');
  const [diffFilter, setDiffFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const filtered = problems.filter(p => {
    if (languageFilter !== 'ALL' && p.language.toUpperCase() !== languageFilter.toUpperCase()) {
      return false;
    }
    if (diffFilter !== 'ALL' && p.difficulty !== diffFilter) {
      return false;
    }
    if (statusFilter === 'SOLVED' && !p.is_solved) {
      return false;
    }
    if (statusFilter === 'UNSOLVED' && p.is_solved) {
      return false;
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchTitle = p.title.toLowerCase().includes(q);
      const matchTopic = (p.topic_name || '').toLowerCase().includes(q);
      const matchCode = (p.course_code || '').toLowerCase().includes(q);
      if (!matchTitle && !matchTopic && !matchCode) return false;
    }
    return true;
  });

  return (
    <div className="bg-[#EAE6DE] border border-[#D7C9B8] rounded-3xl p-4 sm:p-5 shadow-sm space-y-4 text-[#4E3321]">
      {/* ── Search & Filter Header ── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="section-title text-[#2C1B0F] flex items-center gap-2">
            <Filter size={16} className="text-[#60412B]" />
            Syllabus Practice Bank ({filtered.length})
          </h3>
        </div>

        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8C735E]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search problems, topics, or units..."
            className="input w-full pl-8 text-xs font-semibold py-2"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {['ALL', 'JAVA', 'PYTHON', 'JAVASCRIPT', 'SQL'].map(lang => (
            <button
              key={lang}
              onClick={() => onLanguageFilterChange(lang)}
              className={`px-2.5 py-1 rounded-xl text-[10px] font-bold transition-all ${
                languageFilter === lang
                  ? 'bg-[#60412B] text-[#FAF8F5] shadow-sm'
                  : 'bg-[#E5DDC9] text-[#735740] hover:bg-[#D7C9B8]'
              }`}
            >
              {lang === 'ALL' ? 'All Languages' : lang}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between gap-2 pt-1 border-t border-[#D7C9B8]">
          <div className="flex items-center gap-1 text-[11px] font-semibold text-[#8C735E]">
            <span>Difficulty:</span>
            {['ALL', 'EASY', 'MEDIUM', 'HARD'].map(d => (
              <button
                key={d}
                onClick={() => setDiffFilter(d)}
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  diffFilter === d ? 'bg-[#60412B] text-[#FAF8F5]' : 'text-[#735740] hover:bg-[#E5DDC9]'
                }`}
              >
                {d}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1 text-[11px] font-semibold text-[#8C735E]">
            {['ALL', 'UNSOLVED', 'SOLVED'].map(st => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  statusFilter === st ? 'bg-[#60412B] text-[#FAF8F5]' : 'text-[#735740] hover:bg-[#E5DDC9]'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Problem Cards Scroll List ── */}
      <div className="max-h-[380px] overflow-y-auto space-y-2 pr-1">
        {filtered.length > 0 ? (
          filtered.map(p => {
            const isSelected = selectedProblemId === p.id;
            return (
              <button
                key={p.id}
                onClick={() => onSelectProblem(p)}
                className={`w-full text-left p-3 rounded-2xl border transition-all flex items-center justify-between gap-3 ${
                  isSelected
                    ? 'bg-[#60412B] text-[#FAF8F5] border-[#60412B] shadow-md'
                    : 'bg-[#E5DDC9] hover:bg-[#D7C9B8] border-[#D7C9B8] text-[#4E3321]'
                }`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`px-1.5 py-0.5 rounded font-mono text-[9px] font-bold ${
                      isSelected ? 'bg-[#4E3321] text-[#FAF8F5]' : 'bg-[#EAE6DE] text-[#60412B]'
                    }`}>
                      {p.course_code || p.language}
                    </span>
                    <span className={`text-[10px] font-bold ${
                      isSelected ? 'text-[#E5DDC9]' : 'text-[#8C735E]'
                    }`}>
                      {p.difficulty}
                    </span>
                  </div>
                  <div className={`text-xs font-bold truncate ${isSelected ? 'text-[#FAF8F5]' : 'text-[#2C1B0F]'}`}>
                    {p.title}
                  </div>
                  {p.topic_name && (
                    <div className={`text-[10px] font-medium truncate ${isSelected ? 'text-[#D7C9B8]' : 'text-[#8C735E]'}`}>
                      {p.topic_name}
                    </div>
                  )}
                </div>

                <div className="shrink-0 flex items-center gap-1.5">
                  {p.is_solved ? (
                    <CheckCircle2 size={16} className={isSelected ? 'text-[#FAF8F5]' : 'text-[#60412B]'} />
                  ) : (
                    <Circle size={14} className={isSelected ? 'text-[#D7C9B8]' : 'text-[#B09171]'} />
                  )}
                  <ChevronRight size={14} className={isSelected ? 'text-[#FAF8F5]' : 'text-[#B09171]'} />
                </div>
              </button>
            );
          })
        ) : (
          <div className="text-center py-8 text-xs font-semibold text-[#8C735E]">
            No problems match your selected filters.
          </div>
        )}
      </div>
    </div>
  );
};
