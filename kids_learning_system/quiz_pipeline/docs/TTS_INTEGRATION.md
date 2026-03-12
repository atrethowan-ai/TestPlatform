# TTS Integration for Quiz Pipeline

## Overview
This document describes how the quiz_pipeline integrates with the external Kokoro ONNX TTS project for generating audio for `audio_short_answer` questions.

## External Dependency
- **Project:** Kokoro ONNX TTS (voice_agent)
- **Import Path:** `from voice_agent.tts.external_adapter import synthesize_to_file`
- **Function:**
  - `synthesize_to_file(text: str, output_path: str, voice: str | None = None) -> str`
  - Writes a WAV file to `output_path` and returns the path.

## Configuration
- The external TTS project must be available in the Python environment.
- **Recommended:**
  - Install `voice_agent` in editable mode: `pip install -e /path/to/voice_agent`
  - Or add to `PYTHONPATH`.
- The quiz_pipeline does **not** depend directly on Kokoro internals; all calls go through its own wrapper.

## Audio Generation Flow
1. **Authoring input:**
   - Question type: `audio_short_answer`
   - Required: `audioText`
   - Optional: `ttsStyle`, `voice`
2. **Preprocessing:**
   - Validate and normalize fields.
3. **Script building:**
   - Build spoken script based on `ttsStyle` (e.g., `default`, `clear_spelling`).
4. **TTS Synthesis:**
   - Call the TTS adapter (`QuizTTSAdapter`) to generate a temporary WAV and convert to MP3.
   - Write MP3 file to `media/spelling/{quiz_id}/{question_id}.mp3`.
5. **Output:**
   - Inject `mediaRef` (MP3 file path) into the runtime quiz question.
   - Remove authoring-only fields.

## Example Authoring Input
```
{
  "type": "audio_short_answer",
  "audioText": "platform",
  "ttsStyle": "clear_spelling"
}
```

## Example Runtime Output
```
{
  "type": "audio_short_answer",
  "mediaRef": "media/age6/platform.wav"
}
```

## Notes
- All TTS integration is isolated in `engine_existing.py`.
- The pipeline-facing API is in `adapter.py`.
- WAV output is always used.
- Extendable for new TTS engines or styles.
