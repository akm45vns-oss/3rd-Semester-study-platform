import { type FC } from 'react';

export const Skeleton: FC<{ className?: string }> = ({ className = 'h-4 w-full' }) => (
  <div className={`bg-slate-200/80 animate-pulse rounded-md ${className}`} />
);

export const PageSkeleton: FC = () => (
  <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6 animate-fade-in">
    <div className="flex justify-between items-center">
      <Skeleton className="h-6 w-36" />
      <Skeleton className="h-8 w-24 rounded-lg" />
    </div>
    <div className="card p-6 space-y-4">
      <Skeleton className="h-5 w-48" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-9 w-32 rounded-lg mt-2" />
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="card p-5 space-y-3">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="card p-5 space-y-3">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="card p-5 space-y-3">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-full" />
      </div>
    </div>
  </div>
);

export const DashboardSkeleton: FC = () => (
  <div className="space-y-6 animate-fade-in text-slate-800">
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div className="space-y-2">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-7 w-64" />
      </div>
      <Skeleton className="h-9 w-36 rounded-lg" />
    </div>

    {/* Continue Studying Hero Skeleton */}
    <div className="card p-6 space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="h-7 w-72" />
      <Skeleton className="h-4 w-48" />
      <div className="pt-2 flex justify-between items-center">
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-8 w-32 rounded-lg" />
      </div>
    </div>

    {/* Needs Attention Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="card p-5 space-y-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="card p-5 space-y-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-full" />
      </div>
    </div>

    {/* 5 Subject Cards Grid */}
    <div className="space-y-3">
      <Skeleton className="h-4 w-28" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="card p-5 space-y-3">
            <div className="flex justify-between">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-10" />
            </div>
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-2 w-full rounded-full" />
          </div>
        ))}
      </div>
    </div>
  </div>
);

export const TopicWorkspaceSkeleton: FC = () => (
  <div className="space-y-5 animate-fade-in max-w-4xl mx-auto">
    <div className="flex justify-between items-center">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-8 w-24 rounded-lg" />
    </div>

    <div className="card p-5 space-y-3">
      <div className="flex gap-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="h-6 w-80" />
      <Skeleton className="h-2 w-full rounded-full" />
    </div>

    <div className="card p-6 space-y-4 min-h-[300px]">
      <Skeleton className="h-5 w-60" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
    </div>
  </div>
);
