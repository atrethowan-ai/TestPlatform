export interface Quiz {
  id: string;
  title: string;
  ageGroup: string;
  sections: QuizSection[];
  rubricRefs?: string[];
}

export interface QuizSection {
  id: string;
  title: string;
  questions: Question[];
}

export type QuestionType = 'multiple_choice' | 'short_answer' | 'paragraph' | 'audio_short_answer';

export interface Question {
  id: string;
  type: QuestionType;
  prompt: string;
  mediaRef?: string;
  choices?: string[];
  answerKey?: string | string[];
  distractors?: string[];
  rubricRef?: string;
}
