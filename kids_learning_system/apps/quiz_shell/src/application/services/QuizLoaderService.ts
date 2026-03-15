import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export class QuizLoaderService {
  quizzes: any[] = [];
  manifest: { id: string; title: string; ageGroup: string; path: string; category?: string; subcategory?: string; skill?: string; difficulty_level?: number; dateCreated?: string }[] = [];

  async loadAllQuizzes(): Promise<any[]> {
    // Load manifest
    try {
      const manifestRes = await fetch('/quiz_manifest.json');
      if (!manifestRes.ok) throw new Error('Failed to load quiz manifest');
      this.manifest = await manifestRes.json();
    } catch (e) {
      console.error('QuizLoaderService: Could not load quiz_manifest.json', e);
      this.manifest = [];
    }
    // Fetch all quizzes listed in manifest
    const loaded: any[] = [];
    for (const entry of this.manifest) {
      try {
        const res = await fetch(entry.path);
        if (!res.ok) continue;
        const data = await res.json();
        if (data.quizId || data.id) loaded.push(data);
      } catch {}
    }
    this.quizzes = loaded;
    return loaded;
  }

  getAvailableQuizzesForChild(child: { ageBand?: string; childId?: string; isTestUser?: boolean }): any[] {
    if (!this.quizzes.length) return [];
    if (child.childId === 'test-user' || child.ageBand === 'all') {
      return this.quizzes;
    }
    return this.quizzes.filter(q => (q.ageBand || q.ageGroup) === child.ageBand);
  }

  async loadQuizListForChild(child: { ageBand?: string; childId?: string; isTestUser?: boolean }): Promise<{ id: string; title: string; path: string; category: string; subcategory: string; skill: string; difficulty_level: number; dateCreated: string }[]> {
    if (!this.quizzes.length) await this.loadAllQuizzes();
    const filtered = this.getAvailableQuizzesForChild(child);
    // Use manifest to get the correct path/title and taxonomy fields
    return filtered.map(q => {
      const entry = this.manifest.find(m => (m.id === (q.quizId || q.id)));
      return {
        id: q.quizId || q.id,
        title: q.title,
        path: entry ? entry.path : '',
        category: q.category || entry?.category || '',
        subcategory: q.subcategory || entry?.subcategory || '',
        skill: q.skill || entry?.skill || '',
        difficulty_level: q.difficulty_level ?? entry?.difficulty_level ?? 0,
        dateCreated: q.dateCreated || entry?.dateCreated || '',
      };
    });
  }

  async loadQuiz(path: string): Promise<any> {
    try {
      const res = await fetch(path);
      if (!res.ok) {
        const msg = `[QuizLoaderService] Fetch failed: ${res.status} ${res.statusText}`;
        return { error: msg };
      }
      const data = await res.json();
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
