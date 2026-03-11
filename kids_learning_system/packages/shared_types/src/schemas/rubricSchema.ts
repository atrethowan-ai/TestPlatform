import { z } from 'zod';

export const RubricSchema = z.object({
  id: z.string(),
  title: z.string(),
  criteria: z.array(z.object({
    id: z.string(),
    description: z.string(),
    levels: z.array(z.object({
      level: z.string(),
      description: z.string(),
      score: z.number(),
    })),
  })),
});

export type Rubric = z.infer<typeof RubricSchema>;
