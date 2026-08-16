import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard, PublicRoute } from './components/AuthGuard';
import { PageSkeleton } from './components/Skeleton';

// Route-Level Code Splitting (Lazy Loading Heavy Runtimes & Modals)
const AuthPage = lazy(() => import('./pages/AuthPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const SubjectsPage = lazy(() => import('./pages/SubjectsPage'));
const SubjectPage = lazy(() => import('./pages/SubjectPage'));
const TopicPage = lazy(() => import('./pages/TopicPage'));
const PracticeQuizPage = lazy(() => import('./pages/PracticeQuizPage'));
const MistakesPage = lazy(() => import('./pages/MistakesPage'));
const CodingLabPage = lazy(() => import('./pages/CodingLabPage'));
const PracticalsPage = lazy(() => import('./pages/PracticalsPage'));
const RevisionPage = lazy(() => import('./pages/RevisionPage'));
const ExamsPage = lazy(() => import('./pages/ExamsPage'));
const ExamMockPage = lazy(() => import('./pages/ExamMockPage'));

export default function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        {/* Public authentication routes */}
        <Route path="/login" element={<PublicRoute><AuthPage /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><AuthPage /></PublicRoute>} />

        {/* Protected Semester OS routes */}
        <Route path="/dashboard" element={<AuthGuard><DashboardPage /></AuthGuard>} />
        <Route path="/subjects" element={<AuthGuard><SubjectsPage /></AuthGuard>} />
        <Route path="/subjects/:id" element={<AuthGuard><SubjectPage /></AuthGuard>} />
        <Route path="/topics/:id" element={<AuthGuard><TopicPage /></AuthGuard>} />
        <Route path="/practice" element={<AuthGuard><PracticeQuizPage /></AuthGuard>} />
        <Route path="/mistakes" element={<AuthGuard><MistakesPage /></AuthGuard>} />
        <Route path="/coding" element={<AuthGuard><CodingLabPage /></AuthGuard>} />
        <Route path="/practicals" element={<AuthGuard><PracticalsPage /></AuthGuard>} />
        <Route path="/exams" element={<AuthGuard><ExamsPage /></AuthGuard>} />
        <Route path="/exams/mock" element={<AuthGuard><ExamMockPage /></AuthGuard>} />
        <Route path="/revision" element={<AuthGuard><RevisionPage /></AuthGuard>} />

        {/* Default redirects */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}
