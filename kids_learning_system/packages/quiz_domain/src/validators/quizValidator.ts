import type { Quiz } from '@shared_types/src/types/Quiz';
import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export function validateQuiz(quiz: unknown): Quiz {
  return QuizSchema.parse(quiz);
}
