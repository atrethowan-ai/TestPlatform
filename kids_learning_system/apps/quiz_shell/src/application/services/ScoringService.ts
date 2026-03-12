import { Quiz, Question } from '@shared_types/src/types/Quiz';

export interface QuestionEvaluation {
  questionId: string;
  questionNumber: number;
  prompt: string;
  type: Question['type'];
  correctAnswer: string;
  userAnswer: string;
  isCorrect: boolean;
  isGradable: boolean;
}

export function scoreQuiz(quiz: Quiz, answers: Map<string, string>) {
  const questionResults = getQuestionEvaluations(quiz, answers);
  let correct = 0;
  let incorrect = 0;
  let ungraded = 0;
  let total = 0;
  const domainBreakdown: Record<string, { correct: number; total: number }> = {};

  const resultByQuestionId: Record<string, QuestionEvaluation> = {};
  for (const r of questionResults) {
    resultByQuestionId[r.questionId] = r;
  }

  for (const section of quiz.sections) {
    for (const q of section.questions) {
      total++;
      const evalResult = resultByQuestionId[q.id];
      if (evalResult?.isGradable) {
        if (evalResult.isCorrect) {
          correct++;
        } else {
          incorrect++;
        }
      } else {
        ungraded++;
      }

      // Domain breakdown (if q.domain exists)
      if ((q as any).domain) {
        const d = (q as any).domain;
        if (!domainBreakdown[d]) domainBreakdown[d] = { correct: 0, total: 0 };
        domainBreakdown[d].total++;
        if (evalResult?.isGradable && evalResult.isCorrect) {
          domainBreakdown[d].correct++;
        }
      }
    }
  }

  return {
    correct,
    incorrect,
    ungraded,
    total,
    domainBreakdown,
    questionResults,
    resultByQuestionId,
  };
}

export function getQuestionEvaluations(quiz: Quiz, answers: Map<string, string>): QuestionEvaluation[] {
  const evaluations: QuestionEvaluation[] = [];
  let questionNumber = 1;

  for (const section of quiz.sections) {
    for (const q of section.questions) {
      const userAnswer = answers.get(q.id) ?? '';
      const isGradable = q.type !== 'paragraph';
      const isCorrect = isGradable ? isAnswerCorrect(q, userAnswer) : false;

      evaluations.push({
        questionId: q.id,
        questionNumber,
        prompt: q.prompt,
        type: q.type,
        correctAnswer: getCorrectAnswerText(q),
        userAnswer,
        isCorrect,
        isGradable,
      });

      questionNumber++;
    }
  }

  return evaluations;
}

function isAnswerCorrect(question: Question, answer: string): boolean {
  const normalizedAnswer = normalize(answer);
  if (!normalizedAnswer) {
    return false;
  }

  if (question.type === 'multiple_choice') {
    if (typeof question.answerKey !== 'string') return false;
    return normalizedAnswer === normalize(question.answerKey);
  }

  if (question.type === 'short_answer' || question.type === 'audio_short_answer') {
    if (typeof question.answerKey === 'string') {
      return normalizedAnswer === normalize(question.answerKey);
    }
    if (Array.isArray(question.answerKey)) {
      return question.answerKey.some((key: string) => normalizedAnswer === normalize(key));
    }
  }

  return false;
}

function getCorrectAnswerText(question: Question): string {
  if (question.type === 'paragraph') {
    return 'Ungraded';
  }

  if (Array.isArray(question.answerKey)) {
    return question.answerKey.join(' / ');
  }

  if (typeof question.answerKey === 'string') {
    return question.answerKey;
  }

  return '-';
}

function normalize(s: string) {
  return s.trim().toLowerCase();
}
