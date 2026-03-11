// Canonical child model and seed data for kids_learning_system

export interface ChildProfile {
  childId: string;
  displayName: string;
  ageBand?: string;
  isTestUser?: boolean;
  createdAt?: string;
  metadata?: Record<string, any>;
}

export const CHILD_PROFILES: ChildProfile[] = [
  {
    childId: "forrest",
    displayName: "Forrest",
    ageBand: "age9",
    isTestUser: false,
  },
  {
    childId: "homie",
    displayName: "Homie",
    ageBand: "age6",
    isTestUser: false,
  },
  {
    childId: "test-user",
    displayName: "Test User",
    ageBand: "all",
    isTestUser: true,
  },
];
