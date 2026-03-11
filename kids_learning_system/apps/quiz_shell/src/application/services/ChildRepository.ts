import { CHILD_PROFILES, ChildProfile } from '@shared_types/src/types/ChildProfile';

export class ChildRepository {
  private children: ChildProfile[];

  constructor() {
    // In a real app, this could load from IndexedDB or remote, but for now use static seed
    this.children = CHILD_PROFILES;
  }

  getAll(): ChildProfile[] {
    return this.children;
  }

  getById(childId: string): ChildProfile | undefined {
    return this.children.find(c => c.childId === childId);
  }

  isTestUser(childId: string): boolean {
    return this.getById(childId)?.isTestUser === true;
  }
}
