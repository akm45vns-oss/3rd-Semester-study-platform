import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Eye, EyeOff } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { Spinner, ErrorAlert } from '../components/ui';

type Mode = 'login' | 'register';

export default function AuthPage() {
  const [mode, setMode] = useState<Mode>('login');
  const [showPass, setShowPass] = useState(false);
  const [form, setForm] = useState({
    username: '', email: '', password: '', full_name: '',
  });

  const { login, register, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      if (mode === 'login') {
        await login(form.username, form.password);
      } else {
        await register({
          username: form.username,
          email: form.email,
          password: form.password,
          full_name: form.full_name || undefined,
        });
      }
      navigate('/dashboard');
    } catch {
      // error handled by store
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-8 selection:bg-blue-100 selection:text-blue-900">
      <div className="w-full max-w-sm animate-fade-in text-slate-900">
        {/* Logo */}
        <div className="flex flex-col items-center mb-6">
          <div className="w-11 h-11 bg-slate-900 text-white rounded-xl flex items-center justify-center mb-2.5 shadow-sm">
            <GraduationCap className="w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold font-heading text-slate-900 tracking-tight">Semester OS</h1>
          <p className="text-xs text-slate-500 mt-0.5 text-center">
            {mode === 'login' ? 'Sign in to access your curriculum and notes' : 'Create your student study account'}
          </p>
        </div>

        {/* Card */}
        <div className="card p-6 shadow-sm space-y-5">
          {/* Mode toggle */}
          <div className="flex rounded-lg bg-slate-100 p-1 border border-slate-200">
            {(['login', 'register'] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); clearError(); }}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
                  mode === m
                    ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {error && <ErrorAlert message={error} className="mb-4" />}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {mode === 'register' && (
              <div>
                <label htmlFor="full_name" className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Name (optional)
                </label>
                <input
                  id="full_name"
                  type="text"
                  className="input text-xs"
                  placeholder="e.g. Alex Kumar"
                  value={form.full_name}
                  onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                />
              </div>
            )}

            <div>
              <label htmlFor="username" className="block text-xs font-semibold text-slate-700 mb-1">
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                autoComplete="username"
                className="input text-xs font-mono"
                placeholder="e.g. alex45"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
              />
            </div>

            {mode === 'register' && (
              <div>
                <label htmlFor="email" className="block text-xs font-semibold text-slate-700 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  className="input text-xs"
                  placeholder="alex@university.edu"
                  value={form.email}
                  onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                />
              </div>
            )}

            <div>
              <label htmlFor="password" className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPass ? 'text' : 'password'}
                  required
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  className="input text-xs pr-9 font-mono"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(s => !s)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full text-xs py-2.5 font-semibold mt-2 justify-center shadow-sm"
            >
              {isLoading ? (
                <Spinner size="sm" />
              ) : (
                <span>{mode === 'login' ? 'Sign In' : 'Create Account'}</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
