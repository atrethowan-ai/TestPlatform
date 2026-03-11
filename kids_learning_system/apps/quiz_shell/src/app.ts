import { HomeView } from './presentation/views/HomeView';
import { QuizSelectView } from './presentation/views/QuizSelectView';
import { QuizSessionView } from './presentation/views/QuizSessionView';
import { SessionCompleteView } from './presentation/views/SessionCompleteView';
import { QuizLoaderService } from './application/services/QuizLoaderService';
import { createQuizSession } from './application/services/QuizSessionService';
import { scoreQuiz } from './application/services/ScoringService';

let state = {
  view: 'home',
  quizList: [],
  quiz: null,
  session: null,
  sectionIdx: 0,
  questionIdx: 0,
  result: null,
};

const quizLoaderService = new QuizLoaderService();

const root = document.getElementById('app');
if (!root) throw new Error('No #app element found');

async function render() {
  if (state.view === 'home') {
    root.innerHTML = await HomeView({ onStart: () => {} });
    document.getElementById('start-btn')?.addEventListener('click', () => {
      state.view = 'select';
      render();
    });
  } else if (state.view === 'select') {
    const html = await QuizSelectView({ loader: quizLoaderService, onSelect: () => {} });
    root.innerHTML = html;
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
        console.log('[App] Quiz loaded:', quiz.id);
        state.quiz = quiz;
        state.session = createQuizSession(quiz);
        console.log('[App] Session created:', state.session);
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
    root.innerHTML = QuizSessionView({
      quiz,
      sectionIdx,
      questionIdx,
      answers: session.answers,
    });
    const form = document.getElementById('question-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        saveAnswer();
        state.result = scoreQuiz(quiz, session.answers);
        state.view = 'complete';
        render();
      });
      form.querySelectorAll('input[name="answer"],textarea[name="answer"]').forEach(input => {
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
    root.innerHTML = SessionCompleteView({ result: state.result });
    document.getElementById('restart-btn')?.addEventListener('click', () => {
      state.view = 'home';
      state.quiz = null;
      state.session = null;
      state.result = null;
      render();
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
