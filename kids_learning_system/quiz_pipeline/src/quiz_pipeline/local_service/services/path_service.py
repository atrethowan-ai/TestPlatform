from pathlib import Path
import re

def sanitize_filename(s: str) -> str:
    # Remove or replace characters not safe for filenames
    return re.sub(r'[^\w\-_.]', '_', s)

def get_attempt_file_path(base_dir: Path, child_id: str, completed_at: str, quiz_id: str, attempt_id: str) -> Path:
    child_dir = base_dir / sanitize_filename(child_id)
    child_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{sanitize_filename(completed_at)}__{sanitize_filename(quiz_id)}__{sanitize_filename(attempt_id)}.json"
    return child_dir / filename
