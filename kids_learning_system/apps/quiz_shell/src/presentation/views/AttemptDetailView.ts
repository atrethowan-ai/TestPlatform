import { AttemptRepository, AttemptRecord } from '../application/services/AttemptRepository';
import { ChildProfile } from '@shared_types/src/types/ChildProfile';

export async function AttemptDetailView({
  attemptId,
  repo,
  child,
}: {
  attemptId: string;
  repo: AttemptRepository;
  child: ChildProfile;
}) {
  let html = `<div class="container">
    <h2>Attempt Detail</h2>`;
  let attempt: AttemptRecord | undefined;
  try {
    attempt = await repo.getAttemptById(attemptId);
  } catch (err) {
    html += `<div style="color:red;">Failed to load attempt: ${err}</div></div>`;
    return html;
  }
  if (!attempt) {
    html += `<div style="color:red;">Attempt not found.</div></div>`;
    return html;
  }
  html += `<div><b>Child:</b> ${child.displayName}</div>`;
  html += `<div><b>Quiz:</b> ${attempt.quizId}</div>`;
  html += `<div><b>Completed:</b> ${attempt.completedAt}</div>`;
  html += `<div><b>Score:</b> ${attempt.autoScore?.correct ?? 0} / ${attempt.autoScore?.total ?? 0}</div>`;
  html += `<div><b>Status:</b> ${attempt.status}</div>`;
  html += `<h3>Responses</h3><ul>`;
  for (const [qid, resp] of Object.entries(attempt.responses)) {
    html += `<li><b>${qid}:</b> ${JSON.stringify(resp)}</li>`;
  }
  html += `</ul></div>`;
  return html;
}
