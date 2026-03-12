import json
from pathlib import Path
from typing import List
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
