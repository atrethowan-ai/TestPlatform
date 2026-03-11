import type { Attempt } from '@shared_types/src/types/Attempt';
import { getDb } from '../db/indexedDb';

export class AttemptRepository {
  static async get(id: string): Promise<Attempt | undefined> {
    const db = await getDb();
    return db.get('attempts', id);
  }
  static async getAll(): Promise<Attempt[]> {
    const db = await getDb();
    return db.getAll('attempts');
  }
  static async put(attempt: Attempt): Promise<void> {
    const db = await getDb();
    await db.put('attempts', attempt);
  }
  static async getByQuizId(quizId: string): Promise<Attempt[]> {
    const db = await getDb();
    return db.getAllFromIndex('attempts', 'quizId', quizId);
  }
  static async getByChildId(childId: string): Promise<Attempt[]> {
    const db = await getDb();
    return db.getAllFromIndex('attempts', 'childId', childId);
  }
}
