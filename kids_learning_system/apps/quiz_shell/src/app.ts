import { HomeView } from './presentation/views/HomeView';
import { ChildSelectView } from './presentation/views/ChildSelectView';
import { QuizSelectView } from './presentation/views/QuizSelectView';
import { QuizSessionView } from './presentation/views/QuizSessionView';
import { SessionCompleteView } from './presentation/views/SessionCompleteView';
import { QuizLoaderService } from './application/services/QuizLoaderService';
import { createQuizSession } from './application/services/QuizSessionService';
import { scoreQuiz } from './application/services/ScoringService';
import { ChildSelectionService } from './application/services/ChildSelectionService';
import { AttemptRepository } from './application/services/AttemptRepository';
import { HistoryView } from './presentation/views/HistoryView';
import { AttemptDetailView } from './presentation/views/AttemptDetailView';
import { AdminView, AdminSection } from './presentation/views/AdminView';
import { AdminResultsView, loadResultDetail } from './presentation/views/AdminResultsView';
import { AdminQuizBuilderView, wireQuizBuilder } from './presentation/views/AdminQuizBuilderView';
import { AdminQuizManagerView, wireQuizManager } from './presentation/views/AdminQuizManagerView';
import {
  createInitialDecisionTreeTraversalState,
  DecisionTreeTraversalState,
  flattenQuiz,
  FlattenedNavigationNode,
  goBackDecisionTree,
  selectDecisionTreeChoice,
} from './application/services/flattenQuiz';


const DEV_MODE = true; // Set to false for normal runtime

type AppView =
  | 'home'
  | 'child-select'
  | 'select'
  | 'session'
  | 'complete'
  | 'review'
  | 'history'
  | 'attempt-detail'
  | 'admin';

let state: {
  view: AppView;
  quizList: any[];
  quiz: any;
  session: any;
  navigationSequence: FlattenedNavigationNode[];
  navigationIdx: number;
  decisionTreeStateByTreeId: Record<string, DecisionTreeTraversalState>;
  result: any;
  selectedChild: any;
  lastAttemptId: string | null;
  selectedAttemptId: string | null;
  adminSection: AdminSection;
  quizSortMode: 'date' | 'difficulty';
  adminQmSortMode: 'date' | 'difficulty';
} = {
  view: 'home',
  quizList: [],
  quiz: null,
  session: null,
  navigationSequence: [],
  navigationIdx: 0,
  decisionTreeStateByTreeId: {},
  result: null,
  selectedChild: null,
  lastAttemptId: null,
  selectedAttemptId: null,
  adminSection: 'results',
  quizSortMode: 'date',
  adminQmSortMode: 'date',
};

const quizLoaderService = new QuizLoaderService();
const childSelectionService = new ChildSelectionService(DEV_MODE);
const attemptRepository = new AttemptRepository();

const root = document.getElementById('app');
if (!root) throw new Error('No #app element found');

async function render() {
  if (state.view === 'home') {
    root.innerHTML = HomeView();
    document.getElementById('quiz-platform-btn')?.addEventListener('click', () => {
      state.view = 'child-select';
      render();
    });
    document.getElementById('admin-btn')?.addEventListener('click', () => {
      state.view = 'admin';
      renderAdmin(state.adminSection);
    });
  } else if (state.view === 'admin') {
    await renderAdmin(state.adminSection);
  } else if (state.view === 'child-select') {
    const children = childSelectionService.getChildren();
    const selectedChild = childSelectionService.getSelectedChild();
    root.innerHTML = ChildSelectView({
      children,
      selectedChildId: selectedChild?.childId,
      devMode: DEV_MODE,
      onSelect: () => {},
    });
    bindReturnToMain();
    document.querySelectorAll('.child-select-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const childId = (e.target as HTMLElement).getAttribute('data-child-id');
        if (!childId) return;
        childSelectionService.setSelectedChild(childId);
        state.selectedChild = childSelectionService.getSelectedChild();
        state.view = 'select';
        render();
      });
    });
  } else if (state.view === 'select') {
    // Block quiz selection if no child selected
    if (!state.selectedChild) {
      root.innerHTML = `<div class="container">
        <div class="page-header"><button id="return-main-btn" class="return-main-btn">← Main Menu</button></div>
        <h2>No User Selected</h2>
        <div style="color:red;">Please select a user before starting a quiz.</div>
        <button id="select-child-btn" class="btn-primary" style="margin-top:1em;">Select User</button>
      </div>`;
      bindReturnToMain();
      document.getElementById('select-child-btn')?.addEventListener('click', () => {
        state.view = 'child-select';
        render();
      });
      return;
    }
    const html = await QuizSelectView({
      loader: quizLoaderService,
      selectedChild: state.selectedChild,
      onSelect: () => {},
      sortMode: state.quizSortMode,
    });
    root.innerHTML = html;
    bindReturnToMain();
    bindDomainAccordions();
    document.getElementById('sort-date-btn')?.addEventListener('click', () => {
      state.quizSortMode = 'date';
      render();
    });
    document.getElementById('sort-difficulty-btn')?.addEventListener('click', () => {
      state.quizSortMode = 'difficulty';
      render();
    });
    document.querySelectorAll('.quiz-select-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const path = (e.target as HTMLElement).getAttribute('data-path');
        if (!path) return;
        if (DEV_MODE) console.log('[App] Quiz selected:', path);
        const quizOrError = await quizLoaderService.loadQuiz(path);
        if ((quizOrError as any).error) {
          root.innerHTML = `<div class="container">
            <div class="page-header"><button id="return-main-btn" class="return-main-btn">← Main Menu</button></div>
            <h2>Quiz Load Error</h2>
            <div style="color:red;">${(quizOrError as any).error}</div>
            <button id="back-btn" class="btn-secondary" style="margin-top:1em;">Back</button>
          </div>`;
          bindReturnToMain();
          document.getElementById('back-btn')?.addEventListener('click', () => {
            state.view = 'select';
            render();
          });
          return;
        }
        const quiz = quizOrError as any;
        if (DEV_MODE) console.log('[App] Quiz loaded:', quiz.id);
        state.quiz = quiz;
        state.session = createQuizSession(quiz);
        state.navigationSequence = flattenQuiz(quiz);
        state.navigationIdx = 0;
        state.decisionTreeStateByTreeId = createDecisionTreeStateMap(state.navigationSequence);
        state.view = 'session';
        render();
      });
    });
  } else if (state.view === 'session') {
    const quiz = state.quiz;
    const session = state.session;
    const child = state.selectedChild;
    const navNode = getCurrentNavigationNode();
    if (!navNode) {
      root.innerHTML = `<div class="container"><div class="card"><h2>No quiz items found</h2></div></div>`;
      bindReturnToMain();
      return;
    }

    const treeState = navNode.kind === 'decision_tree'
      ? state.decisionTreeStateByTreeId[navNode.treeId]
      : undefined;

    root.innerHTML =
      `<div class="session-header">
        <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
        <span style="color:#444;font-size:0.95em;">User: <b>${child.displayName}</b></span>
      </div>` +
      QuizSessionView({
        quiz,
        navNode,
        navIdx: state.navigationIdx,
        totalNodes: state.navigationSequence.length,
        answers: session.answers,
        readOnly: false,
        decisionTreeTraversalState: treeState,
      });
    bindReturnToMain();

    bindDecisionTreeControls();

    const form = document.getElementById('question-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await completeSession();
      });
      form.querySelectorAll('input[name="answer"],textarea[name="answer"]').forEach(input => {
        input.addEventListener('blur', saveAnswer);
        input.addEventListener('change', saveAnswer);
      });
      form.querySelectorAll('input[name="answer"]').forEach(input => {
        input.addEventListener('keydown', (e: Event) => {
          const keyEvent = e as KeyboardEvent;
          if (keyEvent.key === 'Enter') {
            keyEvent.preventDefault();
          }
        });
      });
    }

    document.getElementById('submit-btn')?.addEventListener('click', async () => {
      saveAnswer();
      await completeSession();
    });

    document.getElementById('next-btn')?.addEventListener('click', () => {
      saveAnswer();
      nextQuestion();
      render();
    });
    document.getElementById('prev-btn')?.addEventListener('click', () => {
      saveAnswer();
      prevQuestion();
      render();
    });
  } else if (state.view === 'complete') {
    const child = state.selectedChild;
    root.innerHTML =
      `<div class="session-header">
        <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
        <span style="color:#444;font-size:0.95em;">User: <b>${child.displayName}</b></span>
      </div>` +
      SessionCompleteView({ result: state.result });
    bindReturnToMain();
    document.getElementById('review-btn')?.addEventListener('click', () => {
      state.navigationIdx = 0;
      state.view = 'review';
      render();
    });
    document.getElementById('restart-btn')?.addEventListener('click', () => {
      state.view = 'home';
      state.quiz = null;
      state.session = null;
      state.navigationSequence = [];
      state.navigationIdx = 0;
      state.decisionTreeStateByTreeId = {};
      state.result = null;
      render();
    });
  } else if (state.view === 'review') {
    const child = state.selectedChild;
    const navNode = getCurrentNavigationNode();
    if (!navNode) {
      root.innerHTML = `<div class="container"><div class="card"><h2>No quiz items found</h2></div></div>`;
      bindReturnToMain();
      return;
    }

    const treeState = navNode.kind === 'decision_tree'
      ? state.decisionTreeStateByTreeId[navNode.treeId]
      : undefined;

    root.innerHTML =
      `<div class="session-header">
        <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
        <span style="color:#444;font-size:0.95em;">User: <b>${child.displayName}</b></span>
      </div>` +
      QuizSessionView({
        quiz: state.quiz,
        navNode,
        navIdx: state.navigationIdx,
        totalNodes: state.navigationSequence.length,
        answers: state.session.answers,
        readOnly: true,
        decisionTreeTraversalState: treeState,
        reviewResultByQuestionId: state.result?.resultByQuestionId,
      });
    bindReturnToMain();
    document.getElementById('next-btn')?.addEventListener('click', () => {
      nextQuestion();
      render();
    });
    document.getElementById('prev-btn')?.addEventListener('click', () => {
      prevQuestion();
      render();
    });
    document.getElementById('back-results-btn')?.addEventListener('click', () => {
      state.view = 'complete';
      render();
    });
  } else if (state.view === 'history') {
    const child = state.selectedChild;
    HistoryView({
      child,
      repo: attemptRepository,
      onSelectAttempt: (attemptId: string) => {
        state.selectedAttemptId = attemptId;
        state.view = 'attempt-detail';
        render();
      },
      devMode: DEV_MODE,
      onClearTestUser: async () => {
        await attemptRepository.clearTestUserHistory();
        render();
      },
    }).then(html => {
      root.innerHTML =
        `<div class="session-header">
          <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
          <span style="color:#444;font-size:0.95em;">User: <b>${child.displayName}</b></span>
        </div>` + html;
      bindReturnToMain();
      document.querySelectorAll('.attempt-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const attemptId = (e.target as HTMLElement).getAttribute('data-attempt-id');
          if (!attemptId) return;
          state.selectedAttemptId = attemptId;
          state.view = 'attempt-detail';
          render();
        });
      });
      if (DEV_MODE && child.childId === 'test-user') {
        document.getElementById('clear-test-user-btn')?.addEventListener('click', async () => {
          await attemptRepository.clearTestUserHistory();
          render();
        });
      }
    });
  } else if (state.view === 'attempt-detail') {
    const child = state.selectedChild;
    const attemptId = state.selectedAttemptId;
    AttemptDetailView({
      attemptId,
      repo: attemptRepository,
      child,
    }).then(html => {
      root.innerHTML =
        `<div class="session-header">
          <button id="return-main-btn" class="return-main-btn">← Main Menu</button>
          <span style="color:#444;font-size:0.95em;">User: <b>${child.displayName}</b></span>
        </div>` +
        html +
        `<div style="margin-top:1em;"><button id="back-to-history-btn" class="btn-secondary">Back to History</button></div>`;
      bindReturnToMain();
      document.getElementById('back-to-history-btn')?.addEventListener('click', () => {
        state.view = 'history';
        render();
      });
    });
  }
}

// -----------------------------------------------------------------------
// Admin rendering
// -----------------------------------------------------------------------

async function renderAdmin(section: AdminSection = state.adminSection) {
  state.adminSection = section;

  let contentHtml = '';
  if (section === 'results') {
    contentHtml = await AdminResultsView();
  } else if (section === 'quiz-builder') {
    contentHtml = AdminQuizBuilderView();
  } else if (section === 'quiz-manager') {
    contentHtml = await AdminQuizManagerView(state.adminQmSortMode);
  }

  root.innerHTML = AdminView(section, contentHtml);

  document.querySelectorAll('.admin-nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const s = (btn as HTMLElement).getAttribute('data-admin-section') as AdminSection;
      if (s) renderAdmin(s);
    });
  });

  bindReturnToMain();

  if (section === 'results') {
    document.querySelectorAll('.result-detail-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const el = btn as HTMLElement;
        const childId = el.dataset.childId || '';
        const filename = el.dataset.filename || '';
        const detail = await loadResultDetail(childId, filename);
        showInfoModal(detail);
      });
    });
  } else if (section === 'quiz-builder') {
    wireQuizBuilder();
  } else if (section === 'quiz-manager') {
    wireQuizManager((mode) => {
      state.adminQmSortMode = mode;
      renderAdmin('quiz-manager');
    });
    document.addEventListener('quiz-archived', () => renderAdmin('quiz-manager'), { once: true });
  }
}

function showInfoModal(html: string) {
  document.getElementById('info-modal-overlay')?.remove();
  const overlay = document.createElement('div');
  overlay.id = 'info-modal-overlay';
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `<div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">Detail</h3>
      <button class="modal-close" id="info-modal-close">✕</button>
    </div>
    <div class="modal-body">${html}</div>
    <div class="modal-footer">
      <button class="btn-secondary" id="info-modal-close-footer">Close</button>
    </div>
  </div>`;
  document.body.appendChild(overlay);
  overlay.querySelector('#info-modal-close')?.addEventListener('click', () => overlay.remove());
  overlay.querySelector('#info-modal-close-footer')?.addEventListener('click', () => overlay.remove());
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

// -----------------------------------------------------------------------
// Shared helpers
// -----------------------------------------------------------------------

function bindReturnToMain() {
  document.getElementById('return-main-btn')?.addEventListener('click', () => {
    state.view = 'home';
    state.quiz = null;
    state.session = null;
    state.navigationSequence = [];
    state.navigationIdx = 0;
    state.decisionTreeStateByTreeId = {};
    state.result = null;
    render();
  });
}

function bindDomainAccordions() {
  document.querySelectorAll('.quiz-domain-header').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = (btn as HTMLElement).getAttribute('data-target');
      if (!target) return;
      const body = document.getElementById(target);
      if (!body) return;
      const expanded = body.style.display !== 'none';
      body.style.display = expanded ? 'none' : 'block';
      btn.setAttribute('aria-expanded', String(!expanded));
      const chevron = btn.querySelector('.quiz-domain-chevron');
      if (chevron) chevron.textContent = expanded ? '▼' : '▲';
    });
  });
}

function saveAnswer() {
  const session = state.session;
  const navNode = getCurrentNavigationNode();
  if (!navNode) return;
  if (navNode.kind !== 'question' && navNode.kind !== 'stimulus_question') {
    return;
  }

  const question = navNode.question;
  const form = document.getElementById('question-form') as HTMLFormElement;
  if (!form) return;

  let value = '';
  if (question.type === 'multiple_choice') {
    const checked = form.querySelector('input[name="answer"]:checked') as HTMLInputElement;
    value = checked ? checked.value : '';
  } else if (question.type === 'short_answer') {
    const input = form.querySelector('input[name="answer"]') as HTMLInputElement;
    value = input ? input.value : '';
  } else if (question.type === 'audio_short_answer') {
    const input = form.querySelector('input[name="answer"]') as HTMLInputElement;
    value = input ? input.value : '';
  } else if (question.type === 'paragraph') {
    const textarea = form.querySelector('textarea[name="answer"]') as HTMLTextAreaElement;
    value = textarea ? textarea.value : '';
  }
  session.answers.set(question.id, value);
}

function nextQuestion() {
  const current = getCurrentNavigationNode();
  if (
    current &&
    current.kind === 'decision_tree' &&
    !state.decisionTreeStateByTreeId[current.treeId]?.reachedEnding
  ) {
    return;
  }

  if (state.navigationIdx < state.navigationSequence.length - 1) {
    state.navigationIdx++;
  }
}

function prevQuestion() {
  if (state.navigationIdx > 0) {
    state.navigationIdx--;
  }
}

function getCurrentNavigationNode(): FlattenedNavigationNode | undefined {
  return state.navigationSequence[state.navigationIdx];
}

function createDecisionTreeStateMap(
  sequence: FlattenedNavigationNode[],
): Record<string, DecisionTreeTraversalState> {
  const map: Record<string, DecisionTreeTraversalState> = {};
  sequence.forEach((node) => {
    if (node.kind === 'decision_tree') {
      map[node.treeId] = createInitialDecisionTreeTraversalState(node.tree);
    }
  });
  return map;
}

function bindDecisionTreeControls() {
  const navNode = getCurrentNavigationNode();
  if (!navNode || navNode.kind !== 'decision_tree') {
    return;
  }

  document.querySelectorAll('.decision-choice-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const choiceId = (btn as HTMLElement).getAttribute('data-choice-id');
      if (!choiceId) {
        return;
      }
      const currentState = state.decisionTreeStateByTreeId[navNode.treeId];
      if (!currentState) {
        return;
      }
      const updated = selectDecisionTreeChoice(
        navNode.tree,
        currentState,
        currentState.currentNodeId,
        choiceId,
      );
      state.decisionTreeStateByTreeId[navNode.treeId] = updated;
      render();
    });
  });

  document.getElementById('tree-back-btn')?.addEventListener('click', () => {
    const currentState = state.decisionTreeStateByTreeId[navNode.treeId];
    if (!currentState) {
      return;
    }
    const updated = goBackDecisionTree(navNode.tree, currentState);
    state.decisionTreeStateByTreeId[navNode.treeId] = updated;
    render();
  });
}

async function completeSession() {
  const quiz = state.quiz;
  const session = state.session;
  const child = state.selectedChild;
  state.result = scoreQuiz(quiz, session.answers);

  const attempt = {
    attemptId: `${child.childId}_${quiz.id}_${Date.now()}`,
    quizId: quiz.id,
    childId: child.childId,
    completedAt: new Date().toISOString(),
    responses: Object.fromEntries(session.answers.entries()),
    score: state.result,
  };

  try {
    await attemptRepository.saveAttempt(attempt);
    try {
      const resp = await fetch('/api/attempts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(attempt),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to save attempt to backend');
      }
    } catch (apiErr) {
      console.warn('Failed to send attempt to backend:', apiErr);
    }
  } catch (err) {
    alert('Failed to save attempt: ' + err);
  }

  state.lastAttemptId = attempt.attemptId;
  state.view = 'complete';
  render();
}


export async function startApp() {
  await render();
}
