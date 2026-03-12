# Authoring Workflow

This document describes the intended workflow for authoring and publishing quizzes.

## Workflow Steps
1. **Quiz results are summarised** (e.g., after a diagnostic)
2. **Summary is pasted into ChatGPT** (or other LLM)
3. **ChatGPT generates a quiz in authoring JSON format** (see quiz_authoring_template.json)
4. **Pipeline validates the authoring quiz**
   - Checks required fields, question types, helper fields
   - Fails with clear error if invalid
5. **Pipeline processes question types**
   - Handles TTS, image, rubric, etc.
6. **Pipeline generates media where needed**
   - TTS for audio_short_answer, images for future types
7. **Pipeline transforms authoring quiz into runtime quiz**
   - Removes authoring-only fields, adds mediaRef
8. **Pipeline publishes runtime quiz + media to the TS system**
   - Copies files to content/quizzes and media folders
9. **Quiz becomes available in the runtime**

## Manual Editing
- Quizzes can be manually edited at any stage before publishing.
- Source-of-truth is the authoring JSON until published.

## Validation
- Occurs before processing and publishing.
- Failures are reported with details for correction.

## Source-of-Truth Files
- **Authoring:** templates/quiz_authoring_template.json, content/quizzes/authoring/
- **Runtime:** content/quizzes/ageX/..., media/ageX/...

## Failure Handling
- If validation or media generation fails, quiz is not published.
- Errors are logged and must be fixed in the authoring JSON.
