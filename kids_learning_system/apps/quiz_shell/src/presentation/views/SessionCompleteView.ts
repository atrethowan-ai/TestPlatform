export function SessionCompleteView({ result }: { result: any }) {
  let html = `<div class="container">
    <h2>Quiz Results</h2>
    <div>Score: ${result.correct} / ${result.total}</div>
    <div>Correct answers: ${result.correct}</div>
    <div>Incorrect answers: ${result.incorrect}</div>
    <div>Ungraded questions: ${result.ungraded}</div>`;
  if (result.domainBreakdown && Object.keys(result.domainBreakdown).length > 0) {
    html += '<h3>Domain Breakdown</h3><ul>';
    for (const [domain, d] of Object.entries(result.domainBreakdown)) {
      html += `<li>${domain}: ${d.correct} / ${d.total}</li>`;
    }
    html += '</ul>';
  }

  if (Array.isArray(result.questionResults) && result.questionResults.length > 0) {
    html += `<h3 style="margin-top:1rem;">Question Review</h3>`;
    html += `<div class="result-review-list">`;
    for (const r of result.questionResults) {
      const userClass = !r.isGradable ? 'ungraded' : (r.isCorrect ? 'correct' : 'incorrect');
      html += `
        <div class="result-review-row">
          <span class="result-badge badge-one">1</span>
          <span class="result-cell">Q${r.questionNumber}</span>
          <span class="result-badge badge-two">2</span>
          <span class="result-cell">${r.correctAnswer || '-'}</span>
          <span class="result-badge badge-three ${userClass}">3</span>
          <span class="result-cell ${userClass}">${r.userAnswer || '(empty)'}</span>
        </div>
      `;
    }
    html += `</div>`;
  }

  html += `<div style="margin-top:1rem;display:flex;gap:0.6rem;flex-wrap:wrap;">
    <button id="review-btn" class="secondary">Review Answers</button>
    <button id="restart-btn" class="primary">Restart</button>
  </div></div>`;
  return html;
}
