import { QuizLoaderService } from '../../application/services/QuizLoaderService';

export async function HomeView({ onStart }: { onStart: () => void }) {
  return `<div class="container">
    <h1>Kids Learning System</h1>
    <button id="start-btn">Start Quiz</button>
  </div>`;
}
