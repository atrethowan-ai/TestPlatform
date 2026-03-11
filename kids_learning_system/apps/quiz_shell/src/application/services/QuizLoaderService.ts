import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export class QuizLoaderService {
  quizzes: any[] = [];
  quizFiles: string[] = [
    '/age6_diagnostic_math_v1.json',
    '/age9_diagnostic_math_v1.json',
  ];

  async loadAllQuizzes(): Promise<any[]> {
    const loaded: any[] = [];
    for (const path of this.quizFiles) {
      try {
        const res = await fetch(path);
        if (!res.ok) continue;
        const data = await res.json();
        // Accept both quizId and id for compatibility
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

  async loadQuizListForChild(child: { ageBand?: string; childId?: string; isTestUser?: boolean }): Promise<{ id: string; title: string; path: string }[]> {
    if (!this.quizzes.length) await this.loadAllQuizzes();
    const filtered = this.getAvailableQuizzesForChild(child);
    return filtered.map(q => ({
      id: q.quizId || q.id,
      title: q.title,
      path: this.quizFiles.find(f => f.includes((q.quizId || q.id).toLowerCase())) || '',
    }));
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
