import { ChildProfile } from '@shared_types/src/types/ChildProfile';

export function ChildSelectView({
  children,
  selectedChildId,
  onSelect,
  devMode = false,
}: {
  children: ChildProfile[];
  selectedChildId?: string;
  onSelect: (childId: string) => void;
  devMode?: boolean;
}) {
  let html = `<div class="container">
    <h2>Select Child</h2>
    <div style="color:#888;font-size:0.9em;margin-bottom:1em;">
      Please select the child who is using the system.<br>
      <b>Test User</b> is for safe testing and development only.
    </div>
    <div class="child-list">`;
  for (const child of children) {
    html += `<button class="child-select-btn" data-child-id="${child.childId}" style="margin:0.5em;padding:1em;${selectedChildId===child.childId?'background:#e0e0e0;':''}">
      ${child.displayName}
      ${child.isTestUser ? '<span style="color:#b00;font-size:0.8em;"> (Test User)</span>' : ''}
    </button>`;
  }
  html += `</div></div>`;
  return html;
}
