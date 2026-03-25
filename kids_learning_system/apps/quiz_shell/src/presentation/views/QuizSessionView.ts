import { Quiz } from '@shared_types/src/types/Quiz';
import { DecisionTreeTraversalState, FlattenedNavigationNode } from '../../application/services/flattenQuiz';
import { renderQuestionPromptHtml } from '../utils/promptRenderer';

interface ReviewResult {
  isCorrect: boolean;
  correctAnswer: string;
  userAnswer: string;
  isGradable: boolean;
}

export function QuizSessionView({
  quiz,
  navNode,
  navIdx,
  totalNodes,
  answers,
  readOnly = false,
  decisionTreeTraversalState,
  reviewResultByQuestionId,
}: {
  quiz: Quiz;
  navNode: FlattenedNavigationNode;
  navIdx: number;
  totalNodes: number;
  answers: Map<string, string>;
  readOnly?: boolean;
  decisionTreeTraversalState?: DecisionTreeTraversalState;
  reviewResultByQuestionId?: Record<string, ReviewResult>;
}) {
  const percent = totalNodes > 0 ? Math.round(((navIdx + 1) / totalNodes) * 100) : 0;
  const progressText = `Step ${navIdx + 1} of ${totalNodes}`;
  const isFirst = navIdx === 0;
  const isLast = navIdx === totalNodes - 1;

  let title = '';
  let promptHtml = '';
  let inputHtml = '';
  let reviewHtml = '';
  let canAdvance = true;

  if (navNode.kind === 'question' || navNode.kind === 'stimulus_question') {
    const question = navNode.question;
    const reviewResult = reviewResultByQuestionId?.[question.id];
    title = quiz.sections[navNode.sectionIdx]?.title ?? 'Quiz';
    promptHtml = renderQuestionPromptHtml(question);
    inputHtml = renderQuestionInput(question, answers, readOnly);
    reviewHtml =
      readOnly && reviewResult
        ? `<div class="review-inline-result ${reviewResult.isGradable ? (reviewResult.isCorrect ? 'correct' : 'incorrect') : 'ungraded'}">${reviewResult.isGradable ? (reviewResult.isCorrect ? 'Correct' : 'Incorrect') : 'Ungraded'} | Correct answer: ${escapeHtml(reviewResult.correctAnswer || '-')} | Your answer: ${escapeHtml(reviewResult.userAnswer || '(empty)')}</div>`
        : '';

    if (navNode.kind === 'stimulus_question') {
      const stimulusTitle = navNode.parentStimulusTitle
        ? `<h3 style="margin-bottom:0.35em;">${escapeHtml(navNode.parentStimulusTitle)}</h3>`
        : '';
      promptHtml = `${stimulusTitle}<div class="quiz-stimulus-text" style="margin-bottom:0.8em;white-space:pre-wrap;">${escapeHtml(navNode.parentStimulusText)}</div><div><b>Q:</b> ${promptHtml}</div>`;
    }
  } else if (navNode.kind === 'stimulus_page') {
    title = navNode.stimulusTitle || 'Read the Passage';
    promptHtml = `<div class="quiz-stimulus-text" style="white-space:pre-wrap;">${escapeHtml(navNode.stimulusText)}</div>`;
  } else if (navNode.kind === 'decision_tree') {
    const tree = navNode.tree;
    const traversalState = decisionTreeTraversalState;
    if (!traversalState) {
      title = tree.title;
      promptHtml = '<div>Decision tree state is unavailable.</div>';
      canAdvance = false;
    } else {
      const currentNode = tree.nodes.find((n) => n.id === traversalState.currentNodeId);
      title = tree.title;
      if (!currentNode) {
        promptHtml = '<div>Current decision-tree node could not be found.</div>';
        canAdvance = false;
      } else if (currentNode.nodeType === 'choice') {
        canAdvance = false;
        const choicesHtml = currentNode.choices
          .map((choice) => {
            const selected = traversalState.choices[currentNode.id] === choice.id;
            if (readOnly) {
              return `<div class="quiz-option-row${selected ? ' selected' : ''} readonly"><span>${escapeHtml(choice.label)}</span></div>`;
            }
            return `<button type="button" class="decision-choice-btn ${selected ? 'primary' : 'secondary'}" data-choice-id="${escapeHtml(choice.id)}">${escapeHtml(choice.label)}</button>`;
          })
          .join('');
        const backButton = !readOnly && traversalState.path.length > 1
          ? '<button type="button" id="tree-back-btn" class="secondary">Back One Step</button>'
          : '';
        promptHtml = `<div style="margin-bottom:0.8em;"><b>Decision:</b> ${escapeHtml(currentNode.prompt)}</div>
          <div style="display:flex;flex-direction:column;gap:0.55em;">${choicesHtml}</div>
          <div style="margin-top:0.9em;">${backButton}</div>`;
      } else {
        canAdvance = true;
        promptHtml = `<h3 style="margin-bottom:0.4em;">${escapeHtml(currentNode.title)}</h3><div style="white-space:pre-wrap;">${escapeHtml(currentNode.conclusion)}</div>`;
      }
    }
  }

  return `<div class="container">
    <div class="card">
      <div style="margin-bottom:0.7em;">
        <div class="quiz-progress-count">${progressText}</div>
        <div class="quiz-progress-bar"><div class="quiz-progress-bar-inner" style="width:${percent}%;"></div></div>
      </div>
      <h2 style="margin-bottom:0.7em;">${escapeHtml(title)}</h2>
      <div class="quiz-prompt" style="font-size:1.15em;margin-bottom:1.2em;">${promptHtml}</div>
      <form id="question-form">
        ${inputHtml}
        ${reviewHtml}
        <div style="margin-top:1.5rem;display:flex;gap:0.7em;">
          ${readOnly ? `<button type="button" id="back-results-btn" class="secondary">Back to Results</button>` : ''}
          <button type="button" id="prev-btn" class="secondary" ${isFirst ? 'disabled' : ''}>Previous</button>
          ${!isLast ? `<button type="button" id="next-btn" class="primary" ${!canAdvance ? 'disabled' : ''}>Next</button>` : ''}
          ${isLast && !readOnly ? `<button type="button" id="submit-btn" class="primary" ${!canAdvance ? 'disabled' : ''}>Submit Quiz</button>` : ''}
        </div>
      </form>
    </div>
  </div>`;
}

function renderQuestionInput(question: any, answers: Map<string, string>, readOnly: boolean): string {
  if (question.type === 'multiple_choice') {
    return `<div class="quiz-options">
      ${question.choices
        ?.map((c: string) => {
          const selected = answers.get(question.id) === c;
          return `<label class="quiz-option-row${selected ? ' selected' : ''}${readOnly ? ' readonly' : ''}">
              <input type="radio" name="answer" value="${escapeHtml(c)}" ${selected ? 'checked' : ''} ${readOnly ? 'disabled' : ''} />
              <span>${escapeHtml(c)}</span>
            </label>`;
        })
        .join('') ?? ''}
    </div>`;
  }

  if (question.type === 'short_answer') {
    return `<input type="text" name="answer" value="${escapeHtml(answers.get(question.id) ?? '')}" ${readOnly ? 'readonly' : ''} />`;
  }

  if (question.type === 'paragraph') {
    return `<textarea name="answer" ${readOnly ? 'readonly' : ''}>${escapeHtml(answers.get(question.id) ?? '')}</textarea>`;
  }

  if (question.type === 'audio_short_answer') {
    return `<div class="audio-question">
      <div class="audio-player-row">
        <audio controls src="${escapeHtml((question as any).mediaRef || '')}">Your browser does not support audio.</audio>
      </div>
      <div class="spelling-answer-row">
        <input type="text" name="answer" value="${escapeHtml(answers.get(question.id) ?? '')}" ${readOnly ? 'readonly' : ''} placeholder="Type your spelling here" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />
      </div>
    </div>`;
  }

  return '';
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
