import { openDB, DBSchema } from 'idb';
import type { Quiz } from '@shared_types/src/types/Quiz';
import type { Attempt } from '@shared_types/src/types/Attempt';
import type { SkillProfile } from '@shared_types/src/types/SkillProfile';
import type { AnalysisArtifact } from '@shared_types/src/types/AnalysisArtifact';
import type { InstructionSet } from '@shared_types/src/types/InstructionSet';

export interface KidsLearningDB extends DBSchema {
  quizzes: {
    key: string;
    value: Quiz;
  };
  attempts: {
    key: string;
    value: Attempt;
    indexes: { quizId: string; childId: string; completedAt: string };
  };
  profiles: {
    key: string;
    value: SkillProfile;
    indexes: { childId: string };
  };
  analyses: {
    key: string;
    value: AnalysisArtifact;
    indexes: { childId: string };
  };
  instructions: {
    key: string;
    value: InstructionSet;
    indexes: { childId: string };
  };
  mediaCatalog: {
    key: string;
    value: { id: string; path: string };
  };
  settings: {
    key: string;
    value: { key: string; value: unknown };
  };
}

export async function getDb() {
  return openDB<KidsLearningDB>('kids_learning_system', 1, {
    upgrade(db) {
      db.createObjectStore('quizzes', { keyPath: 'id' });
      const attempts = db.createObjectStore('attempts', { keyPath: 'id' });
      attempts.createIndex('quizId', 'quizId');
      attempts.createIndex('childId', 'childId');
      attempts.createIndex('completedAt', 'completedAt');
      const profiles = db.createObjectStore('profiles', { keyPath: 'id' });
      profiles.createIndex('childId', 'childId');
      const analyses = db.createObjectStore('analyses', { keyPath: 'id' });
      analyses.createIndex('childId', 'childId');
      const instructions = db.createObjectStore('instructions', { keyPath: 'id' });
      instructions.createIndex('childId', 'childId');
      db.createObjectStore('mediaCatalog', { keyPath: 'id' });
      db.createObjectStore('settings', { keyPath: 'key' });
    },
  });
}
