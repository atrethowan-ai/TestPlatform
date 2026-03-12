import { Quiz, QuizSection } from '@shared_types/src/types/Quiz';

interface ReviewResult {
  isCorrect: boolean;
  correctAnswer: string;
  userAnswer: string;
  isGradable: boolean;
}

export function QuizSessionView({
  quiz,
  sectionIdx,
  questionIdx,
  answers,
  readOnly = false,
  reviewResultByQuestionId,
}: {
  quiz: Quiz;
  sectionIdx: number;
  questionIdx: number;
  answers: Map<string, string>;
  readOnly?: boolean;
  reviewResultByQuestionId?: Record<string, ReviewResult>;
}) {
  const section = quiz.sections[sectionIdx];
  const question = section.questions[questionIdx];
  const reviewResult = reviewResultByQuestionId?.[question.id];
  let inputHtml = '';
  // Flatten all questions for progress
  const allQuestions = quiz.sections.flatMap((s: QuizSection) => s.questions);
  const flatIdx = quiz.sections.slice(0, sectionIdx).reduce((acc: number, s: QuizSection) => acc + s.questions.length, 0) + questionIdx;
  const totalQuestions = allQuestions.length;
  const isFirst = flatIdx === 0;
  const isLast = flatIdx === totalQuestions - 1;
  if (question.type === 'multiple_choice') {
    inputHtml = `<div class="quiz-options">
      ${question.choices
        ?.map(
          (c: string) => {
            const selected = answers.get(question.id) === c;
            return `<label class="quiz-option-row${selected ? ' selected' : ''}${readOnly ? ' readonly' : ''}">
              <input type="radio" name="answer" value="${c}" ${selected ? 'checked' : ''} ${readOnly ? 'disabled' : ''} />
              <span>${c}</span>
            </label>`;
          }
        )
        .join('') ?? ''}
    </div>`;
  } else if (question.type === 'short_answer') {
    inputHtml = `<input type="text" name="answer" value="${answers.get(question.id) ?? ''}" ${readOnly ? 'readonly' : ''} />`;
  } else if (question.type === 'paragraph') {
    inputHtml = `<textarea name="answer" ${readOnly ? 'readonly' : ''}>${answers.get(question.id) ?? ''}</textarea>`;
  } else if (question.type === 'audio_short_answer') {
    inputHtml = `<div class="audio-question">
      <div class="audio-player-row">
        <audio controls src="${(question as any).mediaRef || ''}">Your browser does not support audio.</audio>
      </div>
      <div class="spelling-answer-row">
        <input type="text" name="answer" value="${answers.get(question.id) ?? ''}" ${readOnly ? 'readonly' : ''} placeholder="Type your spelling here" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />
      </div>
    </div>`;
  }
  const percent = Math.round(((flatIdx + 1) / totalQuestions) * 100);
  const progressText = `Question ${flatIdx + 1} of ${totalQuestions}`;
  return `<div class="container">
    <div class="card">
      <div style="margin-bottom:0.7em;">
        <div class="quiz-progress-count">${progressText}</div>
        <div class="quiz-progress-bar"><div class="quiz-progress-bar-inner" style="width:${percent}%;"></div></div>
      </div>
      <h2 style="margin-bottom:0.7em;">${section.title}</h2>
      <div style="font-size:1.15em;margin-bottom:1.2em;"><b>Q:</b> ${question.prompt}</div>
      <form id="question-form">
        ${inputHtml}
        ${readOnly && reviewResult ? `<div class="review-inline-result ${reviewResult.isGradable ? (reviewResult.isCorrect ? 'correct' : 'incorrect') : 'ungraded'}">${reviewResult.isGradable ? (reviewResult.isCorrect ? 'Correct' : 'Incorrect') : 'Ungraded'} | Correct answer: ${reviewResult.correctAnswer || '-'} | Your answer: ${reviewResult.userAnswer || '(empty)'}</div>` : ''}
        <div style="margin-top:1.5rem;display:flex;gap:0.7em;">
          ${readOnly ? `<button type="button" id="back-results-btn" class="secondary">Back to Results</button>` : ''}
          <button type="button" id="prev-btn" class="secondary" ${isFirst ? 'disabled' : ''}>Previous</button>
          ${!isLast ? `<button type="button" id="next-btn" class="primary">Next</button>` : ''}
          ${isLast && !readOnly ? `<button type="submit" id="submit-btn" class="primary">Submit Quiz</button>` : ''}
        </div>
      </form>
    </div>
  </div>`;
}
