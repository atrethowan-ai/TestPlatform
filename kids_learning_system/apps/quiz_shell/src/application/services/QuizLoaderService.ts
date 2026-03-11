import { Quiz, QuizSection, Question } from '@shared_types/src/types/Quiz';
import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export class QuizLoaderService {
  quizzes: Quiz[] = [];

  async loadQuizList(): Promise<{ id: string; title: string; path: string }[]> {
    // Only age9 quiz is available in public for now
    const quizzes = [
      {
        id: 'age9_diagnostic_math_v1',
        title: 'Math Diagnostic (Age 9)',
        path: '/age9_diagnostic_math_v1.json',
      },
    ];
    console.log('[QuizLoaderService] Quiz list:', quizzes);
    return quizzes;
  }

  async loadQuiz(path: string): Promise<Quiz | { error: string }> {
    console.log('[QuizLoaderService] Fetching quiz:', path);
    try {
      const res = await fetch(path);
      if (!res.ok) {
        const msg = `[QuizLoaderService] Fetch failed: ${res.status} ${res.statusText}`;
        console.error(msg);
        return { error: msg };
      }
      const data = await res.json();
      try {
        const quiz = QuizSchema.parse(data);
        console.log('[QuizLoaderService] Quiz validation success:', quiz.id);
        return quiz;
      } catch (err: any) {
        const msg = '[QuizLoaderService] Quiz validation failed: ' + err;
        console.error(msg);
        return { error: msg };
      }
    } catch (err: any) {
      const msg = '[QuizLoaderService] Fetch error: ' + err;
      console.error(msg);
      return { error: msg };
    }
  }
}
