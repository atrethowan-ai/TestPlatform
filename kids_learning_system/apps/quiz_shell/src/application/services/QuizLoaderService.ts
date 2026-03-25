import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export interface QuizListItem {
  id: string;
  title: string;
  path: string;
  category: string;
  subcategory?: string;
  skill?: string;
  difficulty_level: number;
  dateCreated?: string;
  latestScorePercentage?: number | null;
  isNew?: boolean;
}

export interface QuizSubcategoryBucket {
  name: string;
  quizCount: number;
  quizzes: QuizListItem[];
}

export interface QuizCategoryBucket {
  name: string;
  quizCount: number;
  quizzes?: QuizListItem[];
  subcategories: QuizSubcategoryBucket[];
}

export interface QuizSelectionPayload {
  childId: string;
  ageBand: string;
  newQuizzes: QuizListItem[];
  categories: QuizCategoryBucket[];
}

export class QuizLoaderService {
  async loadQuizSelectionForChild(child: { ageBand?: string; childId?: string; isTestUser?: boolean }): Promise<QuizSelectionPayload> {
    const params = new URLSearchParams();
    if (child.childId) params.set('childId', child.childId);
    if (child.ageBand) params.set('ageBand', child.ageBand);

    try {
      const response = await fetch(`/api/quizzes/select?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Failed to load quiz selection payload: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('QuizLoaderService: Could not load select payload', error);
      return {
        childId: child.childId || '',
        ageBand: child.ageBand || '',
        newQuizzes: [],
        categories: [],
      };
    }
  }

  async loadQuiz(path: string): Promise<any> {
    try {
      const res = await fetch(path);
      if (!res.ok) {
        const msg = `[QuizLoaderService] Fetch failed: ${res.status} ${res.statusText}`;
        return { error: msg };
      }
      const rawText = await res.text();
      const cleanText = rawText.replace(/^\uFEFF/, '');
      let data: any;
      try {
        data = JSON.parse(cleanText);
      } catch (parseErr: any) {
        return { error: '[QuizLoaderService] Invalid quiz JSON: ' + parseErr };
      }
      try {
        QuizSchema.parse(data); // Validate
        return data;
      } catch (err: any) {
        return { error: '[QuizLoaderService] Quiz validation failed: ' + err };
      }
    } catch (err: any) {
      return { error: '[QuizLoaderService] Fetch error: ' + err };
    }
  }
}
