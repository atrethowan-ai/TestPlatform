import { z } from 'zod';

export const AnalysisArtifactSchema = z.object({
  id: z.string(),
  childId: z.string(),
  quizId: z.string(),
  createdAt: z.string(),
  summary: z.string(),
  weaknesses: z.array(z.string()),
  recommendations: z.array(z.string()),
});

export type AnalysisArtifact = z.infer<typeof AnalysisArtifactSchema>;
