import { z } from 'zod';

const PromptPartSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('text'),
    text: z.string(),
  }),
  z.object({
    type: z.literal('math'),
    format: z.literal('latex'),
    source: z.string(),
    display: z.enum(['inline', 'block']).optional(),
    altText: z.string(),
  }),
]);

const StandardQuestionSchema = z.object({
  id: z.string(),
  type: z.enum(['multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer']),
  prompt: z.string(),
  promptParts: z.array(PromptPartSchema).optional(),
  subcategory: z.string(),
  skill: z.string(),
  // Legacy compatibility: some previously published quizzes contain domain: null.
  domain: z.string().nullable().optional(),
  mediaRef: z.string().optional(),
  choices: z.array(z.string()).optional(),
  answerKey: z.union([z.string(), z.array(z.string())]).optional(),
  distractors: z.array(z.string()).optional(),
  rubricRef: z.string().optional(),
  audioText: z.string().optional(),
});

const StimulusSetSchema = z.object({
  id: z.string(),
  type: z.literal('stimulus_set'),
  stimulusFormat: z.literal('text'),
  stimulusText: z.string(),
  stimulusTitle: z.string().optional(),
  questions: z.array(StandardQuestionSchema),
});

const DecisionTreeChoiceSchema = z.object({
  id: z.string(),
  label: z.string(),
  nextNodeId: z.string(),
});

const DecisionTreeNodeSchema = z.discriminatedUnion('nodeType', [
  z.object({
    id: z.string(),
    nodeType: z.literal('choice'),
    prompt: z.string(),
    choices: z.array(DecisionTreeChoiceSchema),
  }),
  z.object({
    id: z.string(),
    nodeType: z.literal('ending'),
    title: z.string(),
    conclusion: z.string(),
  }),
]);

const DecisionTreeSchema = z.object({
  id: z.string(),
  type: z.literal('decision_tree'),
  subcategory: z.string(),
  skill: z.string(),
  title: z.string(),
  entryNodeId: z.string(),
  nodes: z.array(DecisionTreeNodeSchema),
});

const QuizItemSchema = z.discriminatedUnion('type', [
  StandardQuestionSchema,
  StimulusSetSchema,
  DecisionTreeSchema,
]);

const QuizSectionSchema = z.object({
  id: z.string(),
  title: z.string(),
  // Legacy section shape.
  questions: z.array(StandardQuestionSchema).optional(),
  // New polymorphic section shape.
  items: z.array(QuizItemSchema).optional(),
}).superRefine((section, ctx) => {
  if (!section.questions && !section.items) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Section must include either 'questions' (legacy) or 'items' (new shape).",
    });
  }
});

export const QuizSchema = z.object({
  id: z.string(),
  title: z.string(),
  ageGroup: z.string(),
  category: z.string(),
  // Legacy optional metadata; taxonomy is enforced per question.
  subcategory: z.string().optional(),
  skill: z.string().optional(),
  difficulty_level: z.number(),
  dateCreated: z.string().optional(),
  sections: z.array(QuizSectionSchema),
  rubricRefs: z.array(z.string()).optional(),
});

export type Quiz = z.infer<typeof QuizSchema>;
