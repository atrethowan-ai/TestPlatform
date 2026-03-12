import { Quiz } from '@shared_types/src/types/Quiz';

export function QuizSessionView({
  quiz,
  sectionIdx,
  questionIdx,
  answers,
}: {
  quiz: Quiz;
  sectionIdx: number;
  questionIdx: number;
  answers: Map<string, string>;
}) {
  const section = quiz.sections[sectionIdx];
  const question = section.questions[questionIdx];
  let inputHtml = '';
  if (question.type === 'multiple_choice') {
    inputHtml = `<div class="quiz-options">
      ${question.choices
        ?.map(
          (c: string) => {
            const selected = answers.get(question.id) === c;
            return `<label class="quiz-option-row${selected ? ' selected' : ''}">
              <input type="radio" name="answer" value="${c}" ${selected ? 'checked' : ''} />
              <span>${c}</span>
            </label>`;
          }
        )
        .join('') ?? ''}
    </div>`;
  } else if (question.type === 'short_answer') {
    inputHtml = `<input type="text" name="answer" value="${answers.get(question.id) ?? ''}" />`;
  } else if (question.type === 'paragraph') {
    inputHtml = `<textarea name="answer">${answers.get(question.id) ?? ''}</textarea>`;
  }
  // Flatten all questions for progress
  const allQuestions = quiz.sections.flatMap(s => s.questions);
  const flatIdx = quiz.sections.slice(0, sectionIdx).reduce((acc, s) => acc + s.questions.length, 0) + questionIdx;
  const totalQuestions = allQuestions.length;
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
        <div style="margin-top:1.5rem;display:flex;gap:0.7em;">
          <button type="button" id="prev-btn" class="secondary" ${isFirst ? 'disabled' : ''}>Previous</button>
          ${!isLast ? `<button type="button" id="next-btn" class="primary">Next</button>` : ''}
          ${isLast ? `<button type="submit" id="submit-btn" class="primary">Submit Quiz</button>` : ''}
        </div>
      </form>
    </div>
  </div>`;
}
