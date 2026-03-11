export interface AnalysisArtifact {
  id: string;
  childId: string;
  quizId: string;
  createdAt: string;
  summary: string;
  weaknesses: string[];
  recommendations: string[];
}
