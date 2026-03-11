export interface Rubric {
  id: string;
  title: string;
  criteria: Array<{
    id: string;
    description: string;
    levels: Array<{
      level: string;
      description: string;
      score: number;
    }>;
  }>;
}
