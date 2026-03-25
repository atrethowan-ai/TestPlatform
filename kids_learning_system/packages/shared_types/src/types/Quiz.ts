export interface Quiz {
  id: string;
  title: string;
  ageGroup: string;
  category: string;
  // Legacy optional metadata; taxonomy is carried per question.
  subcategory?: string;
  skill?: string;
  difficulty_level: number;
  dateCreated?: string;
  sections: QuizSection[];
  rubricRefs?: string[];
}

export interface QuizSection {
  id: string;
  title: string;
  // Legacy section shape.
  questions: Question[];
  // New polymorphic section shape.
  items?: QuizItem[];
}

export type QuestionType = 'multiple_choice' | 'short_answer' | 'paragraph' | 'audio_short_answer';
export type DecisionTreeNodeType = 'choice' | 'ending';

export type PromptPartType = 'text' | 'math';

export interface PromptTextPart {
  type: 'text';
  text: string;
}

export interface PromptMathPart {
  type: 'math';
  format: 'latex';
  source: string;
  display?: 'inline' | 'block';
  altText: string;
}

export type PromptPart = PromptTextPart | PromptMathPart;

export interface Question {
  id: string;
  type: QuestionType;
  prompt: string;
  promptParts?: PromptPart[];
  subcategory: string;
  skill: string;
  mediaRef?: string;
  choices?: string[];
  answerKey?: string | string[];
  distractors?: string[];
  rubricRef?: string;
  // Optional legacy metadata still found in older content.
  domain?: string | null;
  // Required for audio_short_answer.
  audioText?: string;
}

export interface StimulusSet {
  id: string;
  type: 'stimulus_set';
  stimulusFormat: 'text';
  stimulusText: string;
  stimulusTitle?: string;
  // Must contain exactly 3 child questions by validator contract.
  questions: Question[];
}

export interface DecisionTreeChoice {
  id: string;
  label: string;
  nextNodeId: string;
}

export interface DecisionTreeChoiceNode {
  id: string;
  nodeType: 'choice';
  prompt: string;
  choices: DecisionTreeChoice[];
}

export interface DecisionTreeEndingNode {
  id: string;
  nodeType: 'ending';
  title: string;
  conclusion: string;
}

export type DecisionTreeNode = DecisionTreeChoiceNode | DecisionTreeEndingNode;

export interface DecisionTree {
  id: string;
  type: 'decision_tree';
  subcategory: string;
  skill: string;
  title: string;
  entryNodeId: string;
  nodes: DecisionTreeNode[];
}

export type QuizItem = Question | StimulusSet | DecisionTree;
