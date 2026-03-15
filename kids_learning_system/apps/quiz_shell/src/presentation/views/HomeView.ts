export function HomeView() {
  return `<div class="landing-page">
    <div class="landing-hero">
      <h1 class="landing-title">Kids Learning System</h1>
      <p class="landing-subtitle">Interactive quizzes for curious minds</p>
    </div>
    <div class="landing-buttons">
      <button id="quiz-platform-btn" class="landing-btn landing-btn--primary">
        <span class="landing-btn-icon">🎯</span>
        <span class="landing-btn-label">Quiz Platform</span>
        <span class="landing-btn-desc">Start a quiz session</span>
      </button>
      <button id="admin-btn" class="landing-btn landing-btn--admin">
        <span class="landing-btn-icon">⚙️</span>
        <span class="landing-btn-label">Administration</span>
        <span class="landing-btn-desc">Manage quizzes &amp; results</span>
      </button>
    </div>
  </div>`;
}
