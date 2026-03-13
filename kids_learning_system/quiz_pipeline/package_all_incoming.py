"""
Batch package all authoring quizzes in work/incoming/ using the correct TTS CWD and media_root logic.
"""
import os
import sys
import json
from pathlib import Path

SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from quiz_pipeline.package.quiz_packager import package_quiz

VOICE_AGENT_DIR = Path("C:/DEV/260305_ComplexVoiceAgent")
INCOMING_DIR = Path("work/incoming")
GENERATED_DIR = Path("work/generated")

for f in INCOMING_DIR.glob("authoring_spelling_*.json"):
    print(f"\n=== Packaging {f} ===")
    with open(f, "r", encoding="utf-8") as infile:
        authoring_quiz = json.load(infile)
    output_dir = GENERATED_DIR
    original_cwd = os.getcwd()
    os.chdir(VOICE_AGENT_DIR)
    try:
        runtime_quiz = package_quiz(authoring_quiz, output_dir=str(output_dir), media_root=output_dir)
        print(f"Packaged: {f.name} -> {output_dir / authoring_quiz['id'] / (authoring_quiz['id'] + '_runtime.json')}")
    except Exception as e:
        print(f"FAILED: {f.name}: {e}")
    finally:
        os.chdir(original_cwd)
