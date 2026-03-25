import { QuizCategoryBucket, QuizListItem, QuizLoaderService } from '../../application/services/QuizLoaderService';
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
  const selection = await loader.loadQuizSelectionForChild(selectedChild);
  const hasVisibleQuizzes = selection.newQuizzes.length > 0
    || selection.categories.some(category => collectCategoryQuizzes(category).length > 0);

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

  if (!hasVisibleQuizzes) {
    html += `<div class="quiz-select-empty-note">No live quizzes are currently available for this user.</div>`;
  }

  html += renderNewQuizzesSection(sortQuizItems(selection.newQuizzes, sortMode));

  html += `<div class="category-grid">`;

  for (const category of selection.categories) {
    const sortedDomainQuizzes = sortQuizItems(collectCategoryQuizzes(category), sortMode);
    const accordionId = `domain_qs_${category.name}`.replace(/[^a-z0-9]/gi, '_');

    html += `<div class="category-panel">
      <h3 class="category-panel__title">${category.name}</h3>
      <div class="quiz-domain-accordion">
        <button class="quiz-domain-header" aria-expanded="true" data-target="${accordionId}">
          <span>Available Quizzes</span>
          <span class="quiz-domain-count">(${sortedDomainQuizzes.length})</span>
          <span class="quiz-domain-chevron">▲</span>
        </button>
        <div class="quiz-domain-body" id="${accordionId}" style="display:block;">
          ${renderQuizTable(sortedDomainQuizzes, 'No quizzes available in this domain.')}
        </div>
      </div>
    `;

    html += `</div>`;
  }

  html += `</div></div>`;
  return html;
}

function renderNewQuizzesSection(quizzes: QuizListItem[]): string {
  return `<section class="quiz-featured-panel">
    <div class="quiz-featured-panel__header">
      <h3 class="category-panel__title category-panel__title--featured">New Quizzes</h3>
      <p class="quiz-featured-panel__copy">Only quizzes this user has not completed yet.</p>
    </div>
    ${renderQuizTable(quizzes, 'No uncompleted quizzes are currently available.')}
  </section>`;
}

function renderQuizTable(quizzes: QuizListItem[], emptyMessage = 'No quizzes available in this subcategory.'): string {
  const rows = quizzes.length > 0
    ? quizzes.map(renderQuizRow).join('')
    : `<div class="quiz-empty-state">${emptyMessage}</div>`;

  return `${renderQuizHeaderRow()}${rows}`;
}

function renderQuizHeaderRow(): string {
  return `<div class="quiz-row quiz-row--header">
    <span class="quiz-row__title">Title</span>
    <span class="quiz-row__date">Date Created</span>
    <span class="quiz-row__difficulty">Difficulty</span>
    <span class="quiz-row__score">Latest Score</span>
  </div>`;
}

function renderQuizRow(quiz: QuizListItem): string {
  const color = difficultyColor(quiz.difficulty_level || 0);
  const latestScore = typeof quiz.latestScorePercentage === 'number' ? `${quiz.latestScorePercentage}%` : '';
  return `<div class="quiz-row">
    <button class="quiz-select-btn quiz-row__title" data-path="${quiz.path}" data-quiz-id="${quiz.id}">${quiz.title}</button>
    <span class="quiz-row__date">${formatDate(quiz.dateCreated || '')}</span>
    <span class="quiz-row__difficulty"><span class="difficulty-badge" style="background:${color};" title="${difficultyLabel(quiz.difficulty_level || 0)}">${quiz.difficulty_level || '?'}</span></span>
    <span class="quiz-row__score">${latestScore}</span>
  </div>`;
}

function sortQuizItems(quizzes: QuizListItem[], sortMode: SortMode): QuizListItem[] {
  const sorted = [...quizzes];
  if (sortMode === 'date') {
    sorted.sort((a, b) => {
      const dateCompare = (b.dateCreated || '').localeCompare(a.dateCreated || '');
      return dateCompare !== 0 ? dateCompare : a.title.localeCompare(b.title);
    });
    return sorted;
  }

  sorted.sort((a, b) => {
    const difficultyCompare = (a.difficulty_level || 0) - (b.difficulty_level || 0);
    return difficultyCompare !== 0 ? difficultyCompare : a.title.localeCompare(b.title);
  });
  return sorted;
}

function collectCategoryQuizzes(category: QuizCategoryBucket): QuizListItem[] {
  if (category.quizzes && category.quizzes.length > 0) {
    return category.quizzes;
  }
  return category.subcategories.flatMap(subcategory => subcategory.quizzes);
}

