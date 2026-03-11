import { z } from 'zod';

export const QuizSchema = z.object({
  id: z.string(),
  title: z.string(),
  ageGroup: z.string(),
  sections: z.array(z.object({
    id: z.string(),
    title: z.string(),
    questions: z.array(z.object({
      id: z.string(),
      type: z.enum(['multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer']),
      prompt: z.string(),
      mediaRef: z.string().optional(),
      choices: z.array(z.string()).optional(),
      answerKey: z.union([z.string(), z.array(z.string())]).optional(),
      distractors: z.array(z.string()).optional(),
      rubricRef: z.string().optional(),
    })),
  })),
  rubricRefs: z.array(z.string()).optional(),
});

export type Quiz = z.infer<typeof QuizSchema>;
