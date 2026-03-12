from typing import Dict, Any

def summarise_attempts(attempt: Dict[str, Any], quiz: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a quiz review summary with overall stats and per-question review.
    """
    # Build lookup for questionId -> question details
    question_lookup = {}
    for section in quiz.get('sections', []):
        for q in section.get('questions', []):
            qid = q.get('questionId') or q.get('id')
            question_lookup[qid] = q

    responses = attempt.get('responses', {})
    questions_review = []
    total_correct = 0
    total_incorrect = 0
    total_questions = 0

    for qid, q in question_lookup.items():
        prompt = q.get('prompt') or q.get('text') or ''
        correct_answer = q.get('answerKey')
        child_answer = responses.get(qid, None)
        is_correct = (str(child_answer).strip() == str(correct_answer).strip()) if child_answer is not None and correct_answer is not None else False
        questions_review.append({
            'questionId': qid,
            'prompt': prompt,
            'childAnswer': child_answer,
            'correctAnswer': correct_answer,
            'isCorrect': is_correct
        })
        total_questions += 1
        if child_answer is not None:
            if is_correct:
                total_correct += 1
            else:
                total_incorrect += 1

    percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0

    summary = {
        'childId': attempt.get('childId'),
        'quizId': attempt.get('quizId'),
        'completedAt': attempt.get('completedAt'),
        'totalCorrect': total_correct,
        'totalIncorrect': total_incorrect,
        'totalQuestions': total_questions,
        'percentage': percentage,
        'questions': questions_review
    }
    return summary
