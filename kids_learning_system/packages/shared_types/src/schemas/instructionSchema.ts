import { z } from 'zod';

export const InstructionSetSchema = z.object({
  id: z.string(),
  childId: z.string(),
  analysisId: z.string(),
  createdAt: z.string(),
  instructions: z.array(z.string()),
});

export type InstructionSet = z.infer<typeof InstructionSetSchema>;
