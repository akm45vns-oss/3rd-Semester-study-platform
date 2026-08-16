import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertOctagon, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Semester OS Uncaught Error Boundary:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/dashboard';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#E6E0D2] text-[#4E3321] flex items-center justify-center p-4 selection:bg-[#B09171] selection:text-[#FAF8F5]">
          <div className="max-w-md w-full bg-[#EAE6DE] border-2 border-[#D7C9B8] rounded-2xl p-6 sm:p-8 text-center space-y-5 shadow-xl animate-fade-in">
            <div className="w-14 h-14 rounded-2xl bg-[#60412B] text-[#FAF8F5] flex items-center justify-center mx-auto shadow-md">
              <AlertOctagon size={28} />
            </div>

            <div className="space-y-1.5">
              <h1 className="text-xl font-extrabold text-[#2C1B0F]">Something went wrong</h1>
              <p className="text-xs font-semibold text-[#735740] leading-relaxed">
                An unexpected interface error occurred. Your study notes, exam answers, and progress remain safely stored.
              </p>
            </div>

            {this.state.error?.message && (
              <div className="p-3 bg-[#E5DDC9] rounded-xl border border-[#D7C9B8] text-[11px] font-mono text-[#60412B] text-left truncate">
                {this.state.error.message}
              </div>
            )}

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReload}
                className="w-full sm:w-auto btn-primary text-xs py-2.5 px-5 flex items-center justify-center gap-2 shadow"
              >
                <RotateCcw size={14} />
                <span>Reload Application</span>
              </button>

              <button
                onClick={this.handleReset}
                className="w-full sm:w-auto btn-secondary text-xs py-2.5 px-4"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
