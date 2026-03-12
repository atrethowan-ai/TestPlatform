# Question Type Processing

This document describes how each authoring question type is processed by the quiz pipeline.

## 1. multiple_choice
- **Validation:**
  - Must have `choices` (array, min 2)
  - Must have `answerKey` (string or array)
  - Optional: `distractors`, `domain`
- **Processing:**
  - Choices and answerKey are copied to runtime.
  - Distractors are ignored unless used for analytics.
- **Runtime Output:**
  - type, prompt, choices, answerKey, domain

## 2. short_answer
- **Validation:**
  - Must have `answerKey` (string or array)
- **Processing:**
  - answerKey is copied to runtime.
- **Runtime Output:**
  - type, prompt, answerKey

## 3. paragraph
- **Validation:**
  - No answerKey required
  - Optional: `rubricRef`
- **Processing:**
  - rubricRef is copied to runtime if present
- **Runtime Output:**
  - type, prompt, rubricRef (if present)

## 4. audio_short_answer
- **Validation:**
  - Must have `answerKey` (string or array)
  - Must have `audioText` (string)
  - Optional: `ttsStyle`
- **Processing:**
  - Pipeline uses `audioText` and `ttsStyle` to generate TTS audio.
  - If TTS succeeds: writes audio file, sets `mediaRef` to file path, removes authoring-only fields.
  - If `audioText` is missing: validation fails.
  - If TTS fails: pipeline logs error, quiz is not published.
  - If `ttsStyle` is omitted: default style is used.
- **Runtime Output:**
  - type, prompt, answerKey, mediaRef

## Future Types
- `image_short_answer`, `image_multiple_choice` (scaffolded):
  - Will use `imageSpec` for image generation.
  - Not yet implemented.
