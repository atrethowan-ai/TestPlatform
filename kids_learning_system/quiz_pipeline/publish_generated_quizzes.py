"""
Publish all generated spelling quizzes and their media to the frontend:
- Copy runtime JSON to quiz_shell/public/{quiz_id}.json
- Copy MP3s to quiz_shell/dist/media/spelling/{quiz_id}/
"""
import shutil
from pathlib import Path

KIDS_SYSTEM_DIR = Path(__file__).parent.parent
QUIZ_SHELL_PUBLIC = KIDS_SYSTEM_DIR / "apps" / "quiz_shell" / "public"
QUIZ_SHELL_DIST = KIDS_SYSTEM_DIR / "apps" / "quiz_shell" / "dist"
GENERATED_DIR = Path("work/generated")

for quiz_dir in GENERATED_DIR.iterdir():
    if not quiz_dir.is_dir():
        continue
    quiz_id = quiz_dir.name
    runtime_json = quiz_dir / f"{quiz_id}_runtime.json"
    if runtime_json.exists():
        dest_json = QUIZ_SHELL_PUBLIC / f"{quiz_id}.json"
        dest_json.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_json, dest_json)
        print(f"Copied {runtime_json} -> {dest_json}")
    # Copy MP3s
    mp3_dir = GENERATED_DIR / "media" / "spelling" / quiz_id
    if mp3_dir.exists():
        dest_mp3_dir = QUIZ_SHELL_DIST / "media" / "spelling" / quiz_id
        dest_mp3_dir.mkdir(parents=True, exist_ok=True)
        for mp3 in mp3_dir.glob("*.mp3"):
            shutil.copy2(mp3, dest_mp3_dir / mp3.name)
            print(f"Copied {mp3} -> {dest_mp3_dir / mp3.name}")
