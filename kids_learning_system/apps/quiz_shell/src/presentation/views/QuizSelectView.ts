import { QuizLoaderService } from '../../application/services/QuizLoaderService';
import { formatDate, difficultyColor, difficultyLabel } from '../../taxonomy';

type SortMode = 'date' | 'difficulty';

export async function QuizSelectView({
  loader,
  selectedChild,
  onSelect,
  sortMode = 'date',
}: {
  loader: QuizLoaderService;
  selectedChild: any;
  onSelect: (quiz: any) => void;
  sortMode?: SortMode;
}) {
  const quizzes = await loader.loadQuizListForChild(selectedChild);

  let html = `<div class="container quiz-select-container">
    <div class="page-header">
      <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
    </div>
    <h2>Select a Quiz</h2>
    <div class="quiz-select-meta">
      <span><b>User:</b> ${selectedChild?.displayName || 'None'}</span>
      <div class="sort-controls">
        <span class="sort-label">Sort by:</span>
        <button class="sort-btn${sortMode === 'date' ? ' sort-btn--active' : ''}" id="sort-date-btn">Date</button>
        <button class="sort-btn${sortMode === 'difficulty' ? ' sort-btn--active' : ''}" id="sort-difficulty-btn">Difficulty</button>
      </div>
    </div>`;

  if (quizzes.length === 0) {
    html += '<div style="color:#e55;margin-top:1em;">No quizzes found for this user.</div>';
    html += '</div>';
    return html;
  }

  // Sort quizzes
  const sorted = [...quizzes];
  if (sortMode === 'date') {
    sorted.sort((a, b) => (b.dateCreated || '').localeCompare(a.dateCreated || ''));
  } else {
    sorted.sort((a, b) => (a.difficulty_level || 0) - (b.difficulty_level || 0));
  }

  // Group by category → subcategory
  const grouped: Record<string, Record<string, typeof sorted>> = {};
  for (const q of sorted) {
    const cat = q.category || '(Uncategorised)';
    const sub = q.subcategory || '(General)';
    if (!grouped[cat]) grouped[cat] = {};
    if (!grouped[cat][sub]) grouped[cat][sub] = [];
    grouped[cat][sub].push(q);
  }

  html += `<div class="category-grid">`;

  for (const cat of Object.keys(grouped)) {
    html += `<div class="category-panel">
      <h3 class="category-panel__title">${cat}</h3>`;

    for (const sub of Object.keys(grouped[cat])) {
      const items = grouped[cat][sub];
      const subId = `sub_qs_${cat}_${sub}`.replace(/[^a-z0-9]/gi, '_');
      html += `<div class="subcategory-accordion">
        <button class="subcategory-header" aria-expanded="false" data-target="${subId}">
          <span>${sub}</span>
          <span class="subcategory-count">(${items.length})</span>
          <span class="subcategory-chevron">▼</span>
        </button>
        <div class="subcategory-body" id="${subId}" style="display:none;">`;

      for (const q of items) {
        const color = difficultyColor(q.difficulty_level || 0);
        html += `<div class="quiz-row">
          <button class="quiz-select-btn quiz-row__title" data-path="${q.path}" data-quiz-id="${q.id}">${q.title}</button>
          <span class="quiz-row__date">${formatDate(q.dateCreated || '')}</span>
          <span class="quiz-row__difficulty difficulty-badge" style="background:${color};" title="${difficultyLabel(q.difficulty_level || 0)}">${q.difficulty_level || '?'}</span>
        </div>`;
      }

      html += `</div></div>`;
    }

    html += `</div>`;
  }

  html += `</div></div>`;
  return html;
}

