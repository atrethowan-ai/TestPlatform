import { AttemptRepository, AttemptRecord } from '../application/services/AttemptRepository';
import { ChildProfile } from '@shared_types/src/types/ChildProfile';

export async function HistoryView({
  child,
  repo,
  onSelectAttempt,
  devMode = false,
  onClearTestUser,
}: {
  child: ChildProfile;
  repo: AttemptRepository;
  onSelectAttempt: (attemptId: string) => void;
  devMode?: boolean;
  onClearTestUser?: () => void;
}) {
  let html = `<div class="container">
    <h2>History for ${child.displayName}</h2>`;
  if (devMode && child.childId === 'test-user') {
    html += `<button id="clear-test-user-btn" style="background:#fdd;color:#b00;">Clear Test User History</button>`;
  }
  let attempts: AttemptRecord[] = [];
  try {
    attempts = await repo.getAttemptsByChild(child.childId);
  } catch (err) {
    html += `<div style="color:red;">Failed to load history: ${err}</div>`;
    return html + '</div>';
  }
  if (attempts.length === 0) {
    html += `<div style="color:#888;">No attempts found for this child.</div>`;
  } else {
    html += `<ul>`;
    for (const a of attempts) {
      html += `<li><button class="attempt-detail-btn" data-attempt-id="${a.attemptId}">${a.quizId} - ${a.completedAt} - Score: ${a.autoScore?.correct ?? 0}/${a.autoScore?.total ?? 0}</button></li>`;
    }
    html += `</ul>`;
  }
  html += `</div>`;
  return html;
}
