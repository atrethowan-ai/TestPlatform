export interface SkillProfile {
  id: string;
  childId: string;
  createdAt: string;
  skills: Array<{
    skillId: string;
    level: string;
    evidence: string[];
  }>;
}
