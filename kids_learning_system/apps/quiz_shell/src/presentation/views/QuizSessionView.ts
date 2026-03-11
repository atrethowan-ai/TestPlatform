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
    inputHtml = question.choices
      ?.map(
        (c: string) => `<label><input type="radio" name="answer" value="${c}" ${
          answers.get(question.id) === c ? 'checked' : ''
        } /> ${c}</label><br />`,
      )
      .join('') ?? '';
  } else if (question.type === 'short_answer') {
    inputHtml = `<input type="text" name="answer" value="${answers.get(question.id) ?? ''}" />`;
  } else if (question.type === 'paragraph') {
    inputHtml = `<textarea name="answer">${answers.get(question.id) ?? ''}</textarea>`;
  }
  const isFirst = sectionIdx === 0 && questionIdx === 0;
  const isLast = sectionIdx === quiz.sections.length - 1 && questionIdx === section.questions.length - 1;
  return `<div class="container">
    <div style="color:#888;font-size:0.9em;margin-bottom:1em;">
      <div>Quiz ID: ${quiz.id}, Title: ${quiz.title}</div>
      <div>Section: ${sectionIdx + 1}/${quiz.sections.length}, Question: ${questionIdx + 1}/${section.questions.length}</div>
      <div>Session started: ${(quiz as any).startedAt || ''}</div>
    </div>
    <h2>${section.title}</h2>
    <div class="question-card">
      <div><b>Q:</b> ${question.prompt}</div>
      <form id="question-form">
        ${inputHtml}
        <div style="margin-top:1rem;">
          <button type="button" id="prev-btn" ${isFirst ? 'disabled' : ''}>Previous</button>
          ${!isLast ? `<button type="button" id="next-btn">Next</button>` : ''}
          ${isLast ? `<button type="submit" id="submit-btn">Submit Quiz</button>` : ''}
        </div>
      </form>
    </div>
  </div>`;
}
