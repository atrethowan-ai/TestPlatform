import { openDB, IDBPDatabase } from 'idb';
import { ChildProfile } from '@shared_types/src/types/ChildProfile';

export interface AttemptRecord {
  attemptId: string;
  quizId: string;
  childId: string;
  startedAt: string;
  completedAt: string;
  status: string;
  responses: Record<string, any>;
  autoScore: any;
  manualScore?: any;
  metadata?: Record<string, any>;
}

export class AttemptRepository {
  private dbPromise: Promise<IDBPDatabase>;

  constructor() {
    this.dbPromise = openDB('kids_learning_system', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('attempts')) {
          const store = db.createObjectStore('attempts', { keyPath: 'attemptId' });
          store.createIndex('childId', 'childId');
          store.createIndex('quizId', 'quizId');
          store.createIndex('completedAt', 'completedAt');
        }
      },
    });
  }

  async saveAttempt(attempt: AttemptRecord) {
    const db = await this.dbPromise;
    await db.put('attempts', attempt);
  }

  async getAttemptsByChild(childId: string): Promise<AttemptRecord[]> {
    const db = await this.dbPromise;
    return (await db.getAllFromIndex('attempts', 'childId', childId)).sort((a, b) => b.completedAt.localeCompare(a.completedAt));
  }

  async getAttemptById(attemptId: string): Promise<AttemptRecord | undefined> {
    const db = await this.dbPromise;
    return db.get('attempts', attemptId);
  }

  async clearTestUserHistory() {
    const db = await this.dbPromise;
    const all = await db.getAllFromIndex('attempts', 'childId', 'test-user');
    for (const a of all) {
      await db.delete('attempts', a.attemptId);
    }
  }
}
