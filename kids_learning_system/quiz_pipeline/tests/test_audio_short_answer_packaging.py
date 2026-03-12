"""
Test for audio_short_answer packaging flow in isolation.

Verifies:
- authoring quiz with audio_short_answer is transformed to runtime with mediaRef and MP3
- audioText and ttsStyle are removed from runtime
- negative test: missing audioText fails with clear error

Run:
  pytest tests/test_audio_short_answer_packaging.py -v -s
"""
import sys
import os
import shutil
import json
from pathlib import Path
import pytest

SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from quiz_pipeline.transform.authoring_to_runtime import transform_authoring_to_runtime

def clean_media(quiz_id):
    media_dir = Path(f"media/spelling/{quiz_id}")
    if media_dir.exists():
        shutil.rmtree(media_dir)

def test_audio_short_answer_packaging_success():
    quiz_id = "testquiz1"
    clean_media(quiz_id)
    authoring_quiz = {
        "id": quiz_id,
        "title": "Test Quiz",
        "ageGroup": "6-7",
        "sections": [
            {
                "id": "sec1",
                "title": "Section 1",
                "questions": [
                    {
                        "id": "q1",
                        "type": "audio_short_answer",
                        "prompt": "Spell the word shown.",
                        "answerKey": "platform",
                        "audioText": "platform",
                        "ttsStyle": "clear_spelling"
                    }
                ]
            }
        ]
    }
    # Change to voice_agent directory for packaging
    original_cwd = os.getcwd()
    voice_agent_dir = Path("C:/DEV/260305_ComplexVoiceAgent")
    if not voice_agent_dir.exists():
        pytest.skip("voice_agent directory not found: C:/DEV/260305_ComplexVoiceAgent")
    os.chdir(voice_agent_dir)
    try:
        runtime = transform_authoring_to_runtime(authoring_quiz)
    finally:
        os.chdir(original_cwd)
    # Check runtime quiz structure
    assert "sections" in runtime
    q = runtime["sections"][0]["questions"][0]
    assert q["type"] == "audio_short_answer"
    assert "mediaRef" in q
    assert "audioText" not in q
    assert "ttsStyle" not in q
    # Check MP3 file exists
    mp3_path = Path(q["mediaRef"])
    assert mp3_path.exists(), f"MP3 not found: {mp3_path}"
    print(f"PASS: mediaRef and MP3 generated at {mp3_path}")
    # Clean up
    clean_media(quiz_id)

def test_audio_short_answer_packaging_missing_audioText():
    quiz_id = "testquiz2"
    clean_media(quiz_id)
    authoring_quiz = {
        "id": quiz_id,
        "title": "Test Quiz",
        "ageGroup": "6-7",
        "sections": [
            {
                "id": "sec1",
                "title": "Section 1",
                "questions": [
                    {
                        "id": "q1",
                        "type": "audio_short_answer",
                        "prompt": "Spell the word shown.",
                        "answerKey": "platform"
                        # missing audioText
                    }
                ]
            }
        ]
    }
    with pytest.raises(ValueError) as excinfo:
        transform_authoring_to_runtime(authoring_quiz)
    assert "audioText" in str(excinfo.value)
    print(f"PASS: packaging failed as expected: {excinfo.value}")
    # Clean up
    clean_media(quiz_id)

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))
