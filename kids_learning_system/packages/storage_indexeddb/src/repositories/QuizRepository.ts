import type { Quiz } from '@shared_types/src/types/Quiz';
import { getDb } from '../db/indexedDb';

export class QuizRepository {
  static async get(id: string): Promise<Quiz | undefined> {
    const db = await getDb();
    return db.get('quizzes', id);
  }
  static async getAll(): Promise<Quiz[]> {
    const db = await getDb();
    return db.getAll('quizzes');
  }
  static async put(quiz: Quiz): Promise<void> {
    const db = await getDb();
    await db.put('quizzes', quiz);
  }
}
