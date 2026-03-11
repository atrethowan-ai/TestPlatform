import { ChildProfile } from '@shared_types/src/types/ChildProfile';
import { ChildRepository } from './ChildRepository';

export class ChildSelectionService {
  private selectedChild: ChildProfile | null = null;
  private repo: ChildRepository;
  private devMode: boolean;

  constructor(devMode = false) {
    this.repo = new ChildRepository();
    this.devMode = devMode;
    if (devMode) {
      // Default to Test User in dev mode
      this.selectedChild = this.repo.getById('test-user') || null;
    }
  }

  getChildren(): ChildProfile[] {
    return this.repo.getAll();
  }

  getSelectedChild(): ChildProfile | null {
    return this.selectedChild;
  }

  setSelectedChild(childId: string) {
    this.selectedChild = this.repo.getById(childId) || null;
  }

  clearSelection() {
    this.selectedChild = null;
  }
}
