import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..config import settings
from ..models import AttemptPayload, AttemptListItem
from .path_service import get_attempt_file_path, sanitize_filename

def save_attempt(payload: AttemptPayload) -> str:
    file_path = get_attempt_file_path(
        settings.ATTEMPTS_DIR,
        payload.childId,
        payload.completedAt,
        payload.quizId,
        payload.attemptId
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(payload.dict(), f, ensure_ascii=False, indent=2)
    return str(file_path)

def list_attempts(child_id: str) -> List[AttemptListItem]:
    child_dir = settings.ATTEMPTS_DIR / sanitize_filename(child_id)
    if not child_dir.exists() or not child_dir.is_dir():
        return []
    items = []
    for file in child_dir.glob('*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items.append(AttemptListItem(
                filename=file.name,
                attemptId=data.get('attemptId', ''),
                quizId=data.get('quizId', ''),
                completedAt=data.get('completedAt', '')
            ))
        except Exception:
            continue
    return sorted(items, key=lambda x: x.completedAt, reverse=True)


def list_attempt_payloads(child_id: str) -> List[Dict[str, Any]]:
    child_dir = settings.ATTEMPTS_DIR / sanitize_filename(child_id)
    if not child_dir.exists() or not child_dir.is_dir():
        return []

    payloads: List[Dict[str, Any]] = []
    for file in child_dir.glob('*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                payloads.append(json.load(f))
        except Exception:
            continue

    return sorted(payloads, key=lambda x: x.get('completedAt', ''), reverse=True)


def get_latest_score_percentages(child_id: str) -> Dict[str, int]:
    latest_by_quiz: Dict[str, int] = {}
    for payload in list_attempt_payloads(child_id):
        quiz_id = payload.get('quizId') or ''
        if not quiz_id or quiz_id in latest_by_quiz:
            continue

        percentage = _score_to_percentage(payload.get('score'))
        if percentage is None:
            continue
        latest_by_quiz[quiz_id] = percentage

    return latest_by_quiz


def _score_to_percentage(score: Any) -> Optional[int]:
    if not isinstance(score, dict):
        return None

    if _is_positive_number(score.get('total')) and _is_positive_number(score.get('max')):
        return round((float(score['total']) / float(score['max'])) * 100)

    if _is_positive_number(score.get('correct')) and _is_positive_number(score.get('total')):
        return round((float(score['correct']) / float(score['total'])) * 100)

    if _is_positive_number(score.get('percentage')):
        return round(float(score['percentage']))

    return None


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0
