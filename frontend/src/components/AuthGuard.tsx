import { type FC, type ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { PageSkeleton } from '../components/Skeleton';

export const AuthGuard: FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, token, fetchMe } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    if (token && !isAuthenticated) {
      fetchMe();
    }
  }, [token, isAuthenticated, fetchMe]);

  // If token exists in storage but authentication has not finished validating, show skeleton
  if (token && !isAuthenticated) {
    return <PageSkeleton />;
  }

  if (isLoading) return <PageSkeleton />;

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const PublicRoute: FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, token, isLoading, fetchMe } = useAuthStore();

  useEffect(() => {
    if (token && !isAuthenticated) {
      fetchMe();
    }
  }, [token, isAuthenticated, fetchMe]);

  if (token && !isAuthenticated) {
    return <PageSkeleton />;
  }

  if (isLoading) return <PageSkeleton />;

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
