import { type FC, type ReactNode } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LogOut, Flame, ChevronRight, ArrowLeft,
  Home, BookOpen, HelpCircle, Code2, Award,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { StudySessionBar, StudySessionModal } from './StudySessionWidget';

export const AppLayout: FC<{ children: ReactNode }> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 5 Primary Navigation Destinations
  const navCategories = [
    {
      name: 'Home',
      to: '/dashboard',
      icon: Home,
      isActive: location.pathname === '/' || location.pathname === '/dashboard',
    },
    {
      name: 'Subjects',
      to: '/subjects',
      icon: BookOpen,
      isActive: location.pathname.startsWith('/subjects'),
    },
    {
      name: 'Practice',
      to: '/practice',
      icon: HelpCircle,
      isActive: location.pathname.startsWith('/practice') || location.pathname === '/mistakes',
    },
    {
      name: 'Coding Lab',
      to: '/coding',
      icon: Code2,
      isActive: location.pathname.startsWith('/coding') || location.pathname === '/practicals',
    },
    {
      name: 'Exams',
      to: '/exams',
      icon: Award,
      isActive: location.pathname.startsWith('/exams') || location.pathname === '/revision',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-blue-100 selection:text-blue-900 pb-20 md:pb-8">
      {/* ── Desktop Top Header Navigation ── */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-4">
          {/* Logo & Brand Name */}
          <NavLink to="/dashboard" className="flex items-center gap-2.5 group shrink-0">
            <div className="w-8 h-8 sm:w-9 sm:h-9 bg-gradient-to-br from-slate-900 to-blue-950 text-white rounded-lg flex items-center justify-center shadow-sm border border-slate-800">
              <Flame className="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" />
            </div>
            <div>
              <div className="text-sm sm:text-base font-bold text-slate-900 tracking-tight leading-none font-heading">
                StudyForge
              </div>
              <div className="text-[10px] font-medium text-slate-500 mt-0.5 hidden sm:block">
                Engineering Mastery OS
              </div>
            </div>
          </NavLink>

          {/* Desktop Primary Nav Bar */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100/80 p-1 rounded-lg border border-slate-200">
            {navCategories.map((cat) => {
              const Icon = cat.icon;
              return (
                <NavLink
                  key={cat.name}
                  to={cat.to}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                    cat.isActive
                      ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                  }`}
                >
                  <Icon size={14} className={cat.isActive ? 'text-blue-600' : 'text-slate-500'} />
                  <span>{cat.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Right Controls: User Profile & Explicit Logout */}
          <div className="flex items-center gap-2 shrink-0">
            {user ? (
              <div className="flex items-center gap-2">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-xs font-semibold text-slate-900 leading-tight">
                    {user.full_name || user.username}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">
                    Student ID: #{user.id}
                  </span>
                </div>

                <button
                  onClick={handleLogout}
                  className="btn-ghost text-xs p-2 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100"
                  title="Log out of StudyForge"
                >
                  <LogOut size={15} />
                  <span className="hidden sm:inline text-xs font-medium">Log out</span>
                </button>
              </div>
            ) : (
              <NavLink to="/login" className="btn-primary text-xs">
                Log In
              </NavLink>
            )}
          </div>
        </div>
      </header>

      {/* ── Active Study Session Floating Bar ── */}
      <StudySessionBar />
      <StudySessionModal />

      {/* ── Main Application Content Shell ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 sm:py-6">
        {children}
      </main>

      {/* ── Mobile Fixed Bottom Navigation (48px Touch Targets) ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1 flex items-center justify-around shadow-lg">
        {navCategories.map((cat) => {
          const Icon = cat.icon;
          return (
            <NavLink
              key={cat.name}
              to={cat.to}
              className={`flex flex-col items-center justify-center min-w-[56px] min-h-[48px] px-2 py-1 rounded-lg text-[10px] font-semibold transition-all ${
                cat.isActive
                  ? 'text-blue-600 font-bold'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              <Icon size={18} className={cat.isActive ? 'text-blue-600 mb-0.5' : 'text-slate-400 mb-0.5'} />
              <span>{cat.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};

// ── Clean Breadcrumb Navigation Component ──
interface BreadcrumbItem {
  label: string;
  to?: string;
}

export const Breadcrumb: FC<{ items: BreadcrumbItem[] }> = ({ items }) => {
  const navigate = useNavigate();

  // Find previous parent route for mobile back navigation
  const prevItem = items.length > 1 ? items[items.length - 2] : null;

  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-500 py-1">
      {/* Mobile Back Button */}
      {prevItem && (
        <button
          onClick={() => prevItem.to ? navigate(prevItem.to) : navigate(-1)}
          className="sm:hidden flex items-center gap-1 font-semibold text-slate-700 hover:text-slate-900 bg-white px-2.5 py-1 rounded-md border border-slate-200 shadow-sm"
        >
          <ArrowLeft size={13} />
          <span>Back</span>
        </button>
      )}

      {/* Desktop Full Breadcrumb Trail */}
      <nav className="hidden sm:flex items-center gap-1.5 flex-wrap">
        {items.map((item, idx) => {
          const isLast = idx === items.length - 1;
          return (
            <div key={idx} className="flex items-center gap-1.5">
              {idx > 0 && <ChevronRight size={12} className="text-slate-400 shrink-0" />}
              {item.to && !isLast ? (
                <NavLink
                  to={item.to}
                  className="hover:text-slate-900 font-medium transition-colors"
                >
                  {item.label}
                </NavLink>
              ) : (
                <span className={isLast ? 'text-slate-900 font-semibold truncate max-w-[240px]' : 'font-medium'}>
                  {item.label}
                </span>
              )}
            </div>
          );
        })}
      </nav>
    </div>
  );
};
