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
  html += `<button id="restart-btn">Restart</button></div>`;
  return html;
}
