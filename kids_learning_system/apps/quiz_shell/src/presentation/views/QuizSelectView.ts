import { QuizLoaderService } from '../../application/services/QuizLoaderService';

export async function QuizSelectView({ loader, selectedChild, onSelect }: { loader: QuizLoaderService, selectedChild: any, onSelect: (quiz: any) => void }) {
  const quizzes = await loader.loadQuizListForChild(selectedChild);
  let html = `<div class="container"><h2>Select a Quiz</h2>`;
  html += `<div style="color:#888;font-size:0.9em;margin-bottom:1em;">
    <b>Selected Child:</b> ${selectedChild?.displayName || 'None'}<br>
    <b>Available Quizzes:</b> ${quizzes.length}<br>
    <span style="font-size:0.85em;">Discovered ${quizzes.length} quizzes:</span><br>`;
  quizzes.forEach(q => {
    html += `<div>ID: ${q.id}, Title: ${q.title}, Path: ${q.path}</div>`;
  });
  html += '</div>';
  if (quizzes.length === 0) {
    html += '<div style="color:red;">No quizzes found. Check content paths.</div>';
  } else {
    html += '<ul>';
    for (const q of quizzes) {
      html += `<li><button class="quiz-select-btn" data-path="${q.path}">${q.title}</button></li>`;
    }
    html += '</ul>';
  }
  html += '</div>';
  return html;
}
