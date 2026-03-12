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


const DEV_MODE = true; // Set to false for normal runtime

let state = {
  view: 'home',
  quizList: [],
  quiz: null,
  session: null,
  sectionIdx: 0,
  questionIdx: 0,
  result: null,
  selectedChild: null,
};

const quizLoaderService = new QuizLoaderService();
const childSelectionService = new ChildSelectionService(DEV_MODE);
const attemptRepository = new AttemptRepository();

const root = document.getElementById('app');
if (!root) throw new Error('No #app element found');

async function render() {
  if (state.view === 'home') {
    root.innerHTML = await HomeView({ onStart: () => {} });
    document.getElementById('start-btn')?.addEventListener('click', () => {
      state.view = 'child-select';
      render();
    });
  } else if (state.view === 'child-select') {
    const children = childSelectionService.getChildren();
    const selectedChild = childSelectionService.getSelectedChild();
    root.innerHTML = ChildSelectView({
      children,
      selectedChildId: selectedChild?.childId,
      devMode: DEV_MODE,
      onSelect: (childId: string) => {
        childSelectionService.setSelectedChild(childId);
        state.selectedChild = childSelectionService.getSelectedChild();
        state.view = 'select';
        render();
      },
    });
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
      root.innerHTML = `<div class="container"><h2>No Child Selected</h2><div style="color:red;">Please select a child before starting a quiz.</div><button id="select-child-btn">Select Child</button></div>`;
      document.getElementById('select-child-btn')?.addEventListener('click', () => {
        state.view = 'child-select';
        render();
      });
      return;
    }
    const html = await QuizSelectView({ loader: quizLoaderService, selectedChild: state.selectedChild, onSelect: () => {} });
    root.innerHTML = `<div style="margin-bottom:1em;color:#444;">Current Child: <b>${state.selectedChild.displayName}</b></div>` + html;
    document.querySelectorAll('.quiz-select-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const path = (e.target as HTMLElement).getAttribute('data-path');
        if (!path) return;
        console.log('[App] Quiz selected:', path);
        const quizOrError = await quizLoaderService.loadQuiz(path);
        if ((quizOrError as any).error) {
          root.innerHTML = `<div class="container"><h2>Quiz Load Error</h2><div style="color:red;">${(quizOrError as any).error}</div><button id="back-btn">Back</button></div>`;
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
        if (DEV_MODE) console.log('[App] Session created:', state.session);
        state.sectionIdx = 0;
        state.questionIdx = 0;
        state.view = 'session';
        render();
      });
    });
  } else if (state.view === 'session') {
    const quiz = state.quiz;
    const session = state.session;
    const sectionIdx = state.sectionIdx;
    const questionIdx = state.questionIdx;
    const child = state.selectedChild;
    root.innerHTML = `<div style="margin-bottom:1em;color:#444;">Current Child: <b>${child.displayName}</b></div>` +
      QuizSessionView({
        quiz,
        sectionIdx,
        questionIdx,
        answers: session.answers,
      });
    const form = document.getElementById('question-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        saveAnswer();
        state.result = scoreQuiz(quiz, session.answers);
        // Save attempt to IndexedDB
        const attempt = {
          attemptId: `${child.childId}_${quiz.id}_${Date.now()}`,
          quizId: quiz.id,
          childId: child.childId,
          completedAt: new Date().toISOString(),
          responses: Object.fromEntries(session.answers.entries()),
          score: state.result,
          // Optionally add metadata if needed
        };
        try {
          await attemptRepository.saveAttempt(attempt);
          // --- Send attempt to backend API ---
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
            alert('Failed to send attempt to backend: ' + apiErr);
          }
        } catch (err) {
          alert('Failed to save attempt: ' + err);
        }
        state.lastAttemptId = attempt.attemptId;
        state.view = 'complete';
        render();
      });
      form.querySelectorAll('input[name="answer"],textarea[name="answer"]').forEach(input => {
        input.addEventListener('blur', saveAnswer);
        input.addEventListener('change', saveAnswer);
      });
    }
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
    root.innerHTML = `<div style="margin-bottom:1em;color:#444;">Current Child: <b>${child.displayName}</b></div>` +
      SessionCompleteView({ result: state.result });
    document.getElementById('restart-btn')?.addEventListener('click', () => {
      state.view = 'home';
      state.quiz = null;
      state.session = null;
      state.result = null;
      render();
    });
    // Add history and view attempt buttons
    const btns = document.createElement('div');
    btns.innerHTML = `<button id="view-history-btn">View History</button> <button id="view-attempt-btn">View This Attempt</button>`;
    root.querySelector('.container')?.appendChild(btns);
    document.getElementById('view-history-btn')?.addEventListener('click', () => {
      state.view = 'history';
      render();
    });
    document.getElementById('view-attempt-btn')?.addEventListener('click', () => {
      state.view = 'attempt-detail';
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
      root.innerHTML = `<div style="margin-bottom:1em;color:#444;">Current Child: <b>${child.displayName}</b></div>` + html;
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
      root.innerHTML = html + `<div style="margin-top:1em;"><button id="back-to-history-btn">Back to History</button></div>`;
      document.getElementById('back-to-history-btn')?.addEventListener('click', () => {
        state.view = 'history';
        render();
      });
    });
  }
}

function saveAnswer() {
  const quiz = state.quiz;
  const session = state.session;
  const section = quiz.sections[state.sectionIdx];
  const question = section.questions[state.questionIdx];
  const form = document.getElementById('question-form') as HTMLFormElement;
  if (!form) return;
  let value = '';
  if (question.type === 'multiple_choice') {
    const checked = form.querySelector('input[name="answer"]:checked') as HTMLInputElement;
    value = checked ? checked.value : '';
  } else if (question.type === 'short_answer') {
    const input = form.querySelector('input[name="answer"]') as HTMLInputElement;
    value = input ? input.value : '';
  } else if (question.type === 'paragraph') {
    const textarea = form.querySelector('textarea[name="answer"]') as HTMLTextAreaElement;
    value = textarea ? textarea.value : '';
  }
  session.answers.set(question.id, value);
}

function nextQuestion() {
  const quiz = state.quiz;
  let { sectionIdx, questionIdx } = state;
  if (questionIdx < quiz.sections[sectionIdx].questions.length - 1) {
    state.questionIdx++;
  } else if (sectionIdx < quiz.sections.length - 1) {
    state.sectionIdx++;
    state.questionIdx = 0;
  }
}

function prevQuestion() {
  let { sectionIdx, questionIdx } = state;
  if (questionIdx > 0) {
    state.questionIdx--;
  } else if (sectionIdx > 0) {
    state.sectionIdx--;
    state.questionIdx = state.quiz.sections[state.sectionIdx].questions.length - 1;
  }
}


export async function startApp() {
  await render();
}
