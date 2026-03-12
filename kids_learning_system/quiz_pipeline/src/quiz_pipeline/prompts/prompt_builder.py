def build_prompt(summary, quiz=None):
    child_id = summary.get('childId', 'unknown')
    quiz_id = summary.get('quizId', 'unknown')
    completed_at = summary.get('completedAt', 'unknown')
    total_correct = summary.get('totalCorrect', 0)
    total_questions = summary.get('totalQuestions', 0)
    percentage = summary.get('percentage', 0)
    questions = summary.get('questions', [])
    quiz_title = quiz.get('title') if quiz else quiz_id

    lines = [
        f"User: {child_id}",
        f"Date: {completed_at}",
        f"Quiz: {quiz_title}",
        f"",
        f"Score: {total_correct} / {total_questions} ({percentage:.0f}%)",
        f"",
        f"Answers:"
    ]
    for idx, q in enumerate(questions, 1):
        lines.append(f"{idx}. {q['prompt']}")
        lines.append(f"   Your Answer: {q['childAnswer']}")
        lines.append(f"   Correct Answer: {q['correctAnswer']}")
        lines.append(f"   Result: {'Correct' if q['isCorrect'] else 'Incorrect'}\n")
    return "\n".join(lines)
