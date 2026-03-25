"""
After packaging, publish all runtime JSONs and media to the frontend, and generate a manifest.

Important: local runtime serves quiz JSON from quiz_shell/dist, while quiz selection metadata
is built from quiz_shell/public. We therefore keep both trees in sync here.
"""
import json
import shutil
import sys
from pathlib import Path

SRC_PATH = Path(__file__).parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quiz_pipeline.services.encoding_guard import validate_json_file_encoding

KIDS_SYSTEM_DIR = Path(__file__).parent.parent
QUIZ_SHELL_PUBLIC = KIDS_SYSTEM_DIR / "apps" / "quiz_shell" / "public"
QUIZ_SHELL_DIST = KIDS_SYSTEM_DIR / "apps" / "quiz_shell" / "dist"
GENERATED_DIR = Path("work/generated")

manifest = []

for quiz_dir in GENERATED_DIR.iterdir():
    if not quiz_dir.is_dir():
        continue
    quiz_id = quiz_dir.name
    runtime_json = quiz_dir / f"{quiz_id}_runtime.json"
    if runtime_json.exists():
        validate_json_file_encoding(runtime_json)
        # Keep public (authoring/manifest source) and dist (served runtime files) aligned.
        for base_dir in (QUIZ_SHELL_PUBLIC, QUIZ_SHELL_DIST):
            dest_json = base_dir / f"{quiz_id}.json"
            dest_json.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(runtime_json, dest_json)
            print(f"Copied {runtime_json} -> {dest_json}")
        with open(runtime_json, encoding="utf-8") as f:
            quiz_data = json.load(f)
            manifest.append({"id": quiz_id, "title": quiz_data.get("title", quiz_id), "ageGroup": quiz_data.get("ageGroup", "all"), "path": f"/{quiz_id}.json"})
    # Copy MP3s
    mp3_dir = GENERATED_DIR / "media" / "spelling" / quiz_id
    if mp3_dir.exists():
        dest_mp3_dir = QUIZ_SHELL_DIST / "media" / "spelling" / quiz_id
        dest_mp3_dir.mkdir(parents=True, exist_ok=True)
        for mp3 in mp3_dir.glob("*.mp3"):
            shutil.copy2(mp3, dest_mp3_dir / mp3.name)
            print(f"Copied {mp3} -> {dest_mp3_dir / mp3.name}")

# Write manifest into both trees so static-only flows also stay consistent.
for base_dir in (QUIZ_SHELL_PUBLIC, QUIZ_SHELL_DIST):
    manifest_path = base_dir / "quiz_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote manifest: {manifest_path}")
