import { describe, it, expect } from 'vitest';
import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

const validQuiz = {
  id: 'quiz1',
  title: 'Math Diagnostic',
  ageGroup: 'age6',
  sections: [
    {
      id: 'sec1',
      title: 'Numbers',
      questions: [
        {
          id: 'q1',
          type: 'multiple_choice',
          prompt: 'What is 2 + 2?',
          choices: ['3', '4', '5'],
          answerKey: '4',
          distractors: ['3', '5'],
        },
      ],
    },
  ],
};

describe('QuizSchema', () => {
  it('validates a correct quiz', () => {
    expect(() => QuizSchema.parse(validQuiz)).not.toThrow();
  });
  it('fails on missing title', () => {
    const badQuiz = { ...validQuiz };
    // @ts-expect-error
    delete badQuiz.title;
    expect(() => QuizSchema.parse(badQuiz)).toThrow();
  });
});
