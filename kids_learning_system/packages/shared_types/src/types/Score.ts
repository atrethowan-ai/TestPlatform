export interface Score {
  total: number;
  max: number;
  breakdown: { [sectionId: string]: number };
}
