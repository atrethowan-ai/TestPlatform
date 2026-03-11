import { Quiz, Question } from '@shared_types/src/types/Quiz';

export function scoreQuiz(quiz: Quiz, answers: Map<string, string>) {
  let correct = 0;
  let incorrect = 0;
  let ungraded = 0;
  let total = 0;
  const domainBreakdown: Record<string, { correct: number; total: number }> = {};

  for (const section of quiz.sections) {
    for (const q of section.questions) {
      total++;
      const answer = answers.get(q.id);
      if (q.type === 'multiple_choice') {
        if (answer && answer === q.answerKey) {
          correct++;
        } else if (answer) {
          incorrect++;
        } else {
          incorrect++;
        }
      } else if (q.type === 'short_answer') {
        if (answer && typeof q.answerKey === 'string' && normalize(answer) === normalize(q.answerKey)) {
          correct++;
        } else if (answer) {
          incorrect++;
        } else {
          incorrect++;
        }
      } else if (q.type === 'paragraph') {
        ungraded++;
      }
      // Domain breakdown (if q.domain exists)
      if ((q as any).domain) {
        const d = (q as any).domain;
        if (!domainBreakdown[d]) domainBreakdown[d] = { correct: 0, total: 0 };
        domainBreakdown[d].total++;
        if ((q.type === 'multiple_choice' || q.type === 'short_answer') && answer && answer === q.answerKey) {
          domainBreakdown[d].correct++;
        }
      }
    }
  }
  return { correct, incorrect, ungraded, total, domainBreakdown };
}

function normalize(s: string) {
  return s.trim().toLowerCase();
}
