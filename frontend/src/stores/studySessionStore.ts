import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { progressApi } from '../api';
import type { StudySession } from '../types';

interface StudySessionSummary {
  durationMinutes: number;
  topicsStudied: number;
  mcqsAttempted: number;
  accuracyPercent?: number;
  nextTopicName?: string;
  nextTopicId?: number;
}

interface StudySessionState {
  activeSession: StudySession | null;
  startTime: number | null; // unix timestamp ms
  elapsedSeconds: number;
  isPaused: boolean;
  topicsStudiedCount: number;
  mcqsAttemptedCount: number;
  mcqsCorrectCount: number;
  completedSummary: StudySessionSummary | null;

  startSession: (topicId?: number, sessionType?: string) => Promise<void>;
  pauseSession: () => void;
  resumeSession: () => void;
  tick: () => void;
  incrementTopicCount: () => void;
  recordMcqResult: (isCorrect: boolean) => void;
  finishSession: (notes?: string) => Promise<StudySessionSummary | null>;
  clearCompletedSummary: () => void;
}

export const useStudySessionStore = create<StudySessionState>()(
  persist(
    (set, get) => ({
      activeSession: null,
      startTime: null,
      elapsedSeconds: 0,
      isPaused: false,
      topicsStudiedCount: 0,
      mcqsAttemptedCount: 0,
      mcqsCorrectCount: 0,
      completedSummary: null,

      startSession: async (topicId, sessionType = 'THEORY') => {
        try {
          const session = await progressApi.startStudySession({
            topic_id: topicId,
            session_type: sessionType,
          });
          set({
            activeSession: session,
            startTime: Date.now(),
            elapsedSeconds: 0,
            isPaused: false,
            topicsStudiedCount: 1,
            mcqsAttemptedCount: 0,
            mcqsCorrectCount: 0,
            completedSummary: null,
          });
        } catch (e) {
          console.error('Failed to start study session on server, starting locally', e);
          set({
            activeSession: {
              id: Date.now(),
              user_id: 1,
              topic_id: topicId,
              session_type: sessionType,
              duration_minutes: 0,
              started_at: new Date().toISOString(),
            },
            startTime: Date.now(),
            elapsedSeconds: 0,
            isPaused: false,
            topicsStudiedCount: 1,
            mcqsAttemptedCount: 0,
            mcqsCorrectCount: 0,
            completedSummary: null,
          });
        }
      },

      pauseSession: () => set({ isPaused: true }),
      resumeSession: () => set({ isPaused: false }),

      tick: () => {
        const { activeSession, isPaused, elapsedSeconds } = get();
        if (activeSession && !isPaused) {
          set({ elapsedSeconds: elapsedSeconds + 1 });
        }
      },

      incrementTopicCount: () => {
        set(state => ({ topicsStudiedCount: state.topicsStudiedCount + 1 }));
      },

      recordMcqResult: (isCorrect) => {
        set(state => ({
          mcqsAttemptedCount: state.mcqsAttemptedCount + 1,
          mcqsCorrectCount: isCorrect ? state.mcqsCorrectCount + 1 : state.mcqsCorrectCount,
        }));
      },

      finishSession: async (notes) => {
        const { activeSession, elapsedSeconds, topicsStudiedCount, mcqsAttemptedCount, mcqsCorrectCount } = get();
        if (!activeSession) return null;

        const durationMinutes = Math.max(1, Math.round(elapsedSeconds / 60));
        const accuracy = mcqsAttemptedCount > 0 ? Math.round((mcqsCorrectCount / mcqsAttemptedCount) * 100) : undefined;

        try {
          await progressApi.finishStudySession(activeSession.id, {
            notes,
            topics_studied: topicsStudiedCount,
            mcqs_attempted: mcqsAttemptedCount,
          });
        } catch (e) {
          console.error('Failed to finish study session on backend:', e);
        }

        const summary: StudySessionSummary = {
          durationMinutes,
          topicsStudied: topicsStudiedCount,
          mcqsAttempted: mcqsAttemptedCount,
          accuracyPercent: accuracy,
        };

        set({
          activeSession: null,
          startTime: null,
          elapsedSeconds: 0,
          isPaused: false,
          topicsStudiedCount: 0,
          mcqsAttemptedCount: 0,
          mcqsCorrectCount: 0,
          completedSummary: summary,
        });

        return summary;
      },

      clearCompletedSummary: () => set({ completedSummary: null }),
    }),
    {
      name: 'sem_study_session',
      partialize: (state) => ({
        activeSession: state.activeSession,
        startTime: state.startTime,
        elapsedSeconds: state.elapsedSeconds,
        isPaused: state.isPaused,
        topicsStudiedCount: state.topicsStudiedCount,
        mcqsAttemptedCount: state.mcqsAttemptedCount,
        mcqsCorrectCount: state.mcqsCorrectCount,
      }),
    }
  )
);
