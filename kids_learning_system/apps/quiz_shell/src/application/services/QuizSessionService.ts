import { Quiz } from '@shared_types/src/types/Quiz';

export interface QuizSession {
  quizId: string;
  quiz: Quiz;
  answers: Map<string, string>;
  startedAt: string;
  completedAt?: string;
}

export function createQuizSession(quiz: Quiz): QuizSession {
  return {
    quizId: quiz.id,
    quiz,
    answers: new Map(),
    startedAt: new Date().toISOString(),
  };
}
