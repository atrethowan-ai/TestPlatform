import { Score } from './Score';

export interface Attempt {
  id: string;
  quizId: string;
  childId: string;
  startedAt: string;
  completedAt?: string;
  responses: Response[];
  score?: Score;
  manualReviewRequired?: boolean;
}
