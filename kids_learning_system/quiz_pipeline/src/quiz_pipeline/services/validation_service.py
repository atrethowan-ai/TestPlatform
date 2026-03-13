"""
validation_service.py
Authoring quiz validation — used by GUI and CLI.
Returns (errors: list[str], warnings: list[str])
"""

SUPPORTED_TYPES = {'multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer'}
REQUIRED_TOP_LEVEL = ['id', 'title', 'ageGroup', 'sections']


def validate_authoring_quiz(quiz: dict) -> tuple:
    """
    Validate an authoring quiz dict.
    Returns (errors, warnings) where both are lists of strings.
    Errors are fatal; warnings are advisory.
    """
    errors = []
    warnings = []

    if not isinstance(quiz, dict):
        errors.append("Quiz must be a JSON object (dict).")
        return errors, warnings

    # A. Required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in quiz:
            errors.append(f"Missing required top-level field: '{field}'")
        elif quiz[field] in ('', None):
            errors.append(f"Top-level field '{field}' must not be empty.")

    sections = quiz.get('sections')
    if sections is None:
        return errors, warnings

    if not isinstance(sections, list):
        errors.append("'sections' must be a list.")
        return errors, warnings

    if len(sections) == 0:
        errors.append("'sections' must not be empty.")
        return errors, warnings

    # B. Walk sections and questions
    section_ids: set = set()
    question_ids: set = set()
    audio_count = 0

    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            errors.append(f"Section {i + 1} is not an object.")
            continue

        sid = section.get('id', '').strip()
        if not sid:
            errors.append(f"Section {i + 1} missing 'id'.")
        elif sid in section_ids:
            errors.append(f"Duplicate section id: '{sid}'.")
        else:
            section_ids.add(sid)

        questions = section.get('questions', [])
        if not isinstance(questions, list):
            errors.append(f"Section '{sid}' 'questions' must be a list.")
            continue
        if len(questions) == 0:
            warnings.append(f"WARNING: Section '{sid}' has no questions.")
            continue

        for j, q in enumerate(questions):
            if not isinstance(q, dict):
                errors.append(f"Section '{sid}' question {j + 1} is not an object.")
                continue

            qid = q.get('id', '').strip()
            qtype = q.get('type', '').strip()

            if not qid:
                errors.append(f"Section '{sid}' question {j + 1} missing 'id'.")
            elif qid in question_ids:
                errors.append(f"Duplicate question id: '{qid}'.")
            else:
                question_ids.add(qid)

            if not qtype:
                errors.append(f"Question '{qid}' missing 'type'.")
                continue

            if qtype not in SUPPORTED_TYPES:
                warnings.append(f"WARNING: Question '{qid}' has unsupported type: '{qtype}'.")
                continue

            # C. Per-type validation
            if qtype == 'multiple_choice':
                choices = q.get('choices', [])
                if not isinstance(choices, list) or len(choices) < 2:
                    errors.append(f"Question '{qid}' (multiple_choice) must have at least 2 choices.")
                answer_key = q.get('answerKey', '').strip() if q.get('answerKey') else ''
                if not answer_key:
                    errors.append(f"Question '{qid}' (multiple_choice) missing 'answerKey'.")
                elif choices and answer_key not in choices:
                    errors.append(
                        f"Question '{qid}' (multiple_choice) answerKey '{answer_key}' not found in choices."
                    )

            elif qtype == 'short_answer':
                if not q.get('answerKey', '').strip() if isinstance(q.get('answerKey'), str) else not q.get('answerKey'):
                    errors.append(f"Question '{qid}' (short_answer) missing 'answerKey'.")

            elif qtype == 'paragraph':
                if not q.get('prompt', '').strip():
                    errors.append(f"Question '{qid}' (paragraph) missing 'prompt'.")

            elif qtype == 'audio_short_answer':
                audio_count += 1
                if not q.get('audioText', '').strip():
                    errors.append(f"Question '{qid}' (audio_short_answer) missing 'audioText'.")
                ak = q.get('answerKey')
                if not ak or (isinstance(ak, str) and not ak.strip()):
                    errors.append(f"Question '{qid}' (audio_short_answer) missing 'answerKey'.")

    # D. Build readiness info
    if audio_count > 0:
        warnings.append(
            f"INFO: {audio_count} audio_short_answer question(s) detected — "
            f"TTS media will be generated during Build and Publish."
        )

    return errors, warnings
