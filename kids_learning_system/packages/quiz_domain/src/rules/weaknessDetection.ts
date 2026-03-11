import type { Quiz } from '@shared_types/src/types/Quiz';
import type { Attempt } from '@shared_types/src/types/Attempt';

export function detectWeaknesses(quiz: Quiz, attempt: Attempt): string[] {
  // Example: return IDs of questions answered incorrectly
  const wrong: string[] = [];
  for (const section of quiz.sections) {
    for (const q of section.questions) {
      const resp = attempt.responses.find(r => r.questionId === q.id);
      if (!resp || resp.isCorrect === false) {
        wrong.push(q.id);
      }
    }
  }
  return wrong;
}
