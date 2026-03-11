import type { Quiz } from '@shared_types/src/types/Quiz';
import type { Attempt } from '@shared_types/src/types/Attempt';
import type { Response } from '@shared_types/src/types/Response';
import type { Score } from '@shared_types/src/types/Score';

export function scoreAttempt(quiz: Quiz, attempt: Attempt): Score {
  // Simple auto-scoring for MCQ and short_answer
  let total = 0;
  let max = 0;
  const breakdown: Record<string, number> = {};
  for (const section of quiz.sections) {
    let sectionScore = 0;
    for (const q of section.questions) {
      max++;
      const resp = attempt.responses.find(r => r.questionId === q.id);
      if (!resp) continue;
      if (q.type === 'multiple_choice' || q.type === 'short_answer') {
        if (Array.isArray(q.answerKey)) {
          if (Array.isArray(resp.answer) && resp.answer.every(a => q.answerKey!.includes(a))) {
            total++;
            sectionScore++;
          }
        } else if (resp.answer === q.answerKey) {
          total++;
          sectionScore++;
        }
      }
    }
    breakdown[section.id] = sectionScore;
  }
  return { total, max, breakdown };
}
