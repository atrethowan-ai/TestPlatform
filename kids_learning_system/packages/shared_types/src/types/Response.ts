export interface Response {
  questionId: string;
  answer: string | string[];
  submittedAt: string;
  isCorrect?: boolean;
  score?: number;
  manualReviewRequired?: boolean;
}
