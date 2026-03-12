
import logging
from pathlib import Path
from quiz_pipeline.media.tts.question_audio_processor import AudioShortAnswerProcessor

def transform_authoring_to_runtime(authoring_quiz: dict, media_root: Path = None) -> dict:
    """
    Transform authoring quiz JSON to runtime-ready format.
    Generates audio for audio_short_answer questions and injects mediaRef.
    media_root: optional base path where media/spelling/{quiz_id}/ will be written.
    """
    quiz_id = authoring_quiz.get('id')
    if not quiz_id:
        raise ValueError("Quiz is missing 'id'")
    processor = AudioShortAnswerProcessor(quiz_id, media_root=media_root)
    runtime_quiz = {
        'id': authoring_quiz['id'],
        'title': authoring_quiz.get('title'),
        'ageGroup': authoring_quiz.get('ageGroup'),
        'sections': [],
    }
    if 'rubricRefs' in authoring_quiz:
        runtime_quiz['rubricRefs'] = authoring_quiz['rubricRefs']
    for section in authoring_quiz.get('sections', []):
        runtime_section = {
            'id': section['id'],
            'title': section.get('title'),
            'questions': []
        }
        for q in section.get('questions', []):
            qtype = q.get('type')
            qid = q.get('id')
            if not qtype or not qid:
                raise ValueError(f"Question missing 'type' or 'id': {q}")
            runtime_q = {
                'id': qid,
                'type': qtype,
                'prompt': q.get('prompt'),
                'domain': q.get('domain'),
            }
            if 'answerKey' in q:
                runtime_q['answerKey'] = q['answerKey']
            if qtype == 'audio_short_answer':
                logging.info(f"Processing question {qid} (audio_short_answer)")
                if not q.get('audioText'):
                    raise ValueError(f"audio_short_answer question {qid} missing 'audioText'")
                media_ref = processor.process(q)
                runtime_q['mediaRef'] = media_ref
            elif qtype == 'multiple_choice':
                if 'choices' in q:
                    runtime_q['choices'] = q['choices']
                if 'distractors' in q:
                    runtime_q['distractors'] = q['distractors']
            elif qtype == 'short_answer':
                pass  # nothing extra
            elif qtype == 'paragraph':
                if 'rubricRef' in q:
                    runtime_q['rubricRef'] = q['rubricRef']
            # Remove authoring-only fields
            # (audioText, ttsStyle, imageSpec, etc. are not included)
            runtime_section['questions'].append(runtime_q)
        runtime_quiz['sections'].append(runtime_section)
    return runtime_quiz
