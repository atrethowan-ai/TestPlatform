"""
End-to-End test for the spelling quiz pipeline.

Tests the full lifecycle:
  1. Parse authoring JSON
  2. Package quiz (transform + TTS audio generation)
  3. Verify runtime JSON structure and mediaRef
  4. Verify MP3 files are generated
  5. Publish runtime JSON to quiz_shell/public/
  6. Publish MP3 to quiz_shell/dist/media/ (for local service)
  7. Static check: QuizSessionView.ts handles audio_short_answer
  8. Static check: QuizLoaderService.ts registers spelling_test_v1.json
  9. Summarise a synthetic attempt
 10. Verify summary structure

Run with:
  C:/DEV/260311_TestPlatform/.venv/Scripts/python.exe tests/test_e2e_spelling_pipeline.py
from: kids_learning_system/quiz_pipeline/
"""
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# --- path setup ---
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# --- constants ---
QUIZ_PIPELINE_DIR = Path(__file__).parent.parent.resolve()   # .../quiz_pipeline/
KIDS_SYSTEM_DIR   = QUIZ_PIPELINE_DIR.parent                 # .../kids_learning_system/
QUIZ_SHELL_DIR    = KIDS_SYSTEM_DIR / "apps" / "quiz_shell"
VOICE_AGENT_DIR   = Path("C:/DEV/260305_ComplexVoiceAgent")

AUTHORING_FIXTURE = QUIZ_PIPELINE_DIR / "work" / "incoming" / "spelling_test_v1_authoring.json"
GENERATED_DIR     = QUIZ_PIPELINE_DIR / "work" / "generated"
PUBLIC_DIR        = QUIZ_SHELL_DIR / "public"
DIST_DIR          = QUIZ_SHELL_DIR / "dist"

QUIZ_ID           = "spelling_test_v1"
MC_QID            = "mc1"
AUDIO_QID         = "spell1"

# --- helpers ---
results: list[dict] = []

def stage(name: str, passed: bool, detail: str = ""):
    icon = "PASS" if passed else "FAIL"
    results.append({"stage": name, "passed": passed, "detail": detail})
    print(f"  [{icon}] {name}" + (f"\n         {detail}" if detail else ""))

def skip(name: str, reason: str = ""):
    results.append({"stage": name, "passed": None, "detail": reason})
    print(f"  [SKIP] {name}" + (f" - {reason}" if reason else ""))


# ============================================================
# STAGE 1: Load authoring quiz
# ============================================================
print("\n=== STAGE 1: Parse authoring quiz ===")
try:
    with open(AUTHORING_FIXTURE, "r", encoding="utf-8") as f:
        authoring_quiz = json.load(f)
    ok = (
        authoring_quiz.get("id") == QUIZ_ID
        and any(
            q.get("type") == "audio_short_answer"
            for s in authoring_quiz.get("sections", [])
            for q in s.get("questions", [])
        )
    )
    stage("Load authoring fixture", ok, f"id={authoring_quiz.get('id')}")
except Exception as e:
    stage("Load authoring fixture", False, str(e))
    authoring_quiz = None

if not authoring_quiz:
    print("\nAbort: Cannot continue without authoring quiz.")
    sys.exit(1)


# ============================================================
# STAGE 2: Package quiz (transform + TTS)
# ============================================================
print("\n=== STAGE 2: Package quiz (transform + TTS) ===")
runtime_quiz = None
try:
    from quiz_pipeline.package.quiz_packager import package_quiz

    output_dir = str(GENERATED_DIR)
    media_root = GENERATED_DIR

    original_cwd = os.getcwd()
    os.chdir(VOICE_AGENT_DIR)
    try:
        runtime_quiz = package_quiz(authoring_quiz, output_dir=output_dir, media_root=media_root)
    finally:
        os.chdir(original_cwd)

    stage("package_quiz returned", runtime_quiz is not None)
except Exception as e:
    stage("package_quiz", False, str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# STAGE 3: Verify runtime JSON structure
# ============================================================
print("\n=== STAGE 3: Verify runtime JSON ===")
runtime_path = GENERATED_DIR / QUIZ_ID / f"{QUIZ_ID}_runtime.json"

try:
    with open(runtime_path, "r", encoding="utf-8") as f:
        saved_runtime = json.load(f)
    stage("Runtime JSON written to disk", True, str(runtime_path))
except Exception as e:
    stage("Runtime JSON written to disk", False, str(e))
    saved_runtime = runtime_quiz  # fallback to in-memory

rq = saved_runtime or runtime_quiz
if rq:
    stage("Runtime has correct id", rq.get("id") == QUIZ_ID)
    all_q = [q for s in rq.get("sections", []) for q in s.get("questions", [])]
    stage("Runtime has expected question count", len(all_q) == 2, f"{len(all_q)} questions")

    audio_qs = [q for q in all_q if q.get("type") == "audio_short_answer"]
    if audio_qs:
        aq = audio_qs[0]
        has_media_ref = bool(aq.get("mediaRef"))
        no_audio_text = "audioText" not in aq
        no_tts_style  = "ttsStyle" not in aq
        stage("audio_short_answer has mediaRef", has_media_ref, aq.get("mediaRef", "(missing)"))
        stage("audioText stripped from runtime", no_audio_text)
        stage("ttsStyle stripped from runtime",  no_tts_style)
    else:
        stage("audio_short_answer question exists in runtime", False, "not found")


# ============================================================
# STAGE 4: Verify MP3 generated
# ============================================================
print("\n=== STAGE 4: Verify MP3 ===")
expected_mp3 = GENERATED_DIR / "media" / "spelling" / QUIZ_ID / f"{AUDIO_QID}.mp3"
if expected_mp3.exists():
    size = expected_mp3.stat().st_size
    stage("MP3 file exists", True, f"{expected_mp3} ({size} bytes)")
    stage("MP3 is non-empty", size > 0, f"{size} bytes")
else:
    stage("MP3 file exists", False, str(expected_mp3))


# ============================================================
# STAGE 5: Publish to quiz_shell/public/
# ============================================================
print("\n=== STAGE 5: Publish runtime JSON to quiz_shell/public/ ===")
dest_json = PUBLIC_DIR / f"{QUIZ_ID}.json"
try:
    if rq:
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        with open(dest_json, "w", encoding="utf-8") as f:
            json.dump(rq, f, indent=2)
        stage("Runtime JSON copied to public/", True, str(dest_json))
    else:
        stage("Runtime JSON copied to public/", False, "No runtime quiz available")
except Exception as e:
    stage("Runtime JSON copied to public/", False, str(e))


# ============================================================
# STAGE 6: Publish MP3 to quiz_shell/dist/media/
# ============================================================
print("\n=== STAGE 6: Publish MP3 to quiz_shell/dist/ ===")
dest_mp3 = DIST_DIR / "media" / "spelling" / QUIZ_ID / f"{AUDIO_QID}.mp3"
try:
    if expected_mp3.exists():
        dest_mp3.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(expected_mp3, dest_mp3)
        stage("MP3 copied to dist/media/", True, str(dest_mp3))
    else:
        stage("MP3 copied to dist/media/", False, "Source MP3 missing (Stage 4 failed)")
except Exception as e:
    stage("MP3 copied to dist/media/", False, str(e))


# ============================================================
# STAGE 7: Static check – QuizSessionView.ts
# ============================================================
print("\n=== STAGE 7: Frontend – QuizSessionView.ts ===")
quiz_session_view = QUIZ_SHELL_DIR / "src" / "presentation" / "views" / "QuizSessionView.ts"
try:
    src = quiz_session_view.read_text(encoding="utf-8")
    has_audio_case = "audio_short_answer" in src
    has_audio_tag  = "<audio" in src
    stage("QuizSessionView handles audio_short_answer type", has_audio_case)
    stage("QuizSessionView renders <audio> element", has_audio_tag)
except Exception as e:
    stage("QuizSessionView.ts readable", False, str(e))


# ============================================================
# STAGE 8: Static check – QuizLoaderService.ts
# ============================================================
print("\n=== STAGE 8: Frontend – QuizLoaderService.ts ===")
quiz_loader = QUIZ_SHELL_DIR / "src" / "application" / "services" / "QuizLoaderService.ts"
try:
    src = quiz_loader.read_text(encoding="utf-8")
    registered = f"{QUIZ_ID}.json" in src
    stage(f"QuizLoaderService registers {QUIZ_ID}.json", registered)
except Exception as e:
    stage("QuizLoaderService.ts readable", False, str(e))


# ============================================================
# STAGE 9: Summarise a synthetic attempt
# ============================================================
print("\n=== STAGE 9: Summarise synthetic attempt ===")
summary = None
try:
    from quiz_pipeline.extract.attempt_summariser import summarise_attempts

    synthetic_attempt = {
        "childId": "test-child-01",
        "quizId":  QUIZ_ID,
        "completedAt": datetime.utcnow().isoformat() + "Z",
        "responses": {
            MC_QID:    "Blue",
            AUDIO_QID: "platform",
        }
    }

    target_quiz = rq if rq else None
    if target_quiz:
        summary = summarise_attempts(synthetic_attempt, target_quiz)
        stage("summarise_attempts completed", summary is not None)
    else:
        skip("summarise_attempts", "No runtime quiz available")
except Exception as e:
    stage("summarise_attempts", False, str(e))
    import traceback
    traceback.print_exc()


# ============================================================
# STAGE 10: Verify summary structure
# ============================================================
print("\n=== STAGE 10: Verify summary ===")
if summary:
    stage("Summary has totalCorrect",    "totalCorrect"    in summary, str(summary.get("totalCorrect")))
    stage("Summary has totalQuestions",  "totalQuestions"  in summary, str(summary.get("totalQuestions")))
    stage("Summary has percentage",      "percentage"      in summary, f"{summary.get('percentage')}%")
    stage("Summary has questions list",  isinstance(summary.get("questions"), list),
          f"{len(summary.get('questions', []))} items")
    correct = summary.get("totalCorrect", 0)
    stage("Both answers scored correctly", correct == 2, f"totalCorrect={correct}")
    print("\n--- Full Summary ---")
    print(json.dumps(summary, indent=2))
else:
    skip("Summary structure checks", "No summary produced")


# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 60)
print("FINAL CHECKLIST")
print("=" * 60)
passed  = [r for r in results if r["passed"] is True]
failed  = [r for r in results if r["passed"] is False]
skipped = [r for r in results if r["passed"] is None]
for r in results:
    icon = "PASS" if r["passed"] is True else ("FAIL" if r["passed"] is False else "SKIP")
    print(f"  [{icon}] {r['stage']}" + (f"\n         => {r['detail']}" if r.get("detail") and not r["passed"] else ""))
print(f"\n  Total: {len(passed)} PASS | {len(failed)} FAIL | {len(skipped)} SKIP")
if failed:
    print("\n  FAILED stages:")
    for r in failed:
        print(f"    - {r['stage']}: {r.get('detail','')}")
print("=" * 60)
sys.exit(0 if not failed else 1)
