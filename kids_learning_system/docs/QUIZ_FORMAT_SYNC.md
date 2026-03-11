# QUIZ_FORMAT_SYNC

## A. Source Files Inspected

- apps/quiz_shell/src/application/services/QuizLoaderService.ts
- apps/quiz_shell/src/presentation/views/QuizSessionView.ts
- apps/quiz_shell/src/application/services/ScoringService.ts
- packages/quiz_domain/src/validators/quizValidator.ts
- packages/quiz_domain/src/rules/scoring.ts
- packages/shared_types/src/schemas/quizSchema.ts
- packages/shared_types/src/types/Quiz.ts
- content/quizzes/age6/age6_diagnostic_math_v1.json
- content/quizzes/age9/age9_diagnostic_math_v1.json
- docs/SCHEMAS.md
- docs/CONTENT_PACKAGES.md

## B. Actual Current Runtime Quiz Schema (Plain English)

- Root quiz object:
  - id (string)
  - title (string)
  - ageGroup (string)
  - sections (array of Section)
  - rubricRefs (optional array of string)

- Section object:
  - id (string)
  - title (string)
  - questions (array of Question)

- Question object:
  - id (string)
  - type ("multiple_choice" | "short_answer" | "paragraph" | "audio_short_answer")
  - prompt (string)
  - mediaRef (optional string)
  - choices (optional array of string)
  - answerKey (optional string or array of string)
  - distractors (optional array of string)
  - rubricRef (optional string)

## C. Example Canonical Quiz JSON

See docs/QUIZ_FORMAT_EXAMPLE.json for a cleaned canonical example.

## D. Field-by-Field Notes

### Quiz Root
- id: string, required, used in code as quiz.id (sample JSON uses quizId)
- title: string, required, used
- ageGroup: string, required, used (sample JSON uses ageBand)
- sections: array, required, used
- rubricRefs: array of string, optional, used if present

### Section
- id: string, required, used (sample JSON uses sectionId)
- title: string, required, used
- questions: array, required, used

### Question
- id: string, required, used (sample JSON uses questionId)
- type: string, required, used ('multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer')
- prompt: string, required, used
- mediaRef: string, optional, used for audio questions
- choices: array of string, optional, used for multiple_choice
- answerKey: string or array, optional, used for scoring
- distractors: array of string, optional, used for playful options
- rubricRef: string, optional, used for paragraph/manual review
- domain: present in sample JSON, used in scoring breakdown, not in schema
- points: present in sample JSON, ignored in runtime

### Sample JSON Mismatches
- quizId vs id
- ageBand vs ageGroup
- sectionId vs id
- questionId vs id
- options vs choices
- domain: used in scoring breakdown, not in schema
- points: present, not used
- description: present, not used
- estimatedDurationMinutes: present, not used

## E. Mismatches / Drift

- Sample JSON uses quizId, ageBand, sectionId, questionId, options (not id, ageGroup, id, id, choices)
- Schema expects id, ageGroup, choices, etc.
- Fields like domain, points, description, estimatedDurationMinutes are present in JSON but not in schema
- Scoring logic uses domain if present, but schema does not require it
- answerKey can be string or array, but sample JSON always uses string

## F. Recommendations

- Python pipeline should emit quiz files with:
  - id (not quizId)
  - ageGroup (not ageBand)
  - sections[].id (not sectionId)
  - questions[].id (not questionId)
  - questions[].choices (not options)
- Optional fields: mediaRef, distractors, rubricRef, answerKey
- domain and points: can be included, but not required by schema
- description, estimatedDurationMinutes: ignored by runtime, can be included for metadata
- answerKey: support both string and array
- Ensure all required fields are present and match schema

## Canonical Example

See docs/QUIZ_FORMAT_EXAMPLE.json for a canonical example.

---

# Summary

- The current real schema expects id, ageGroup, choices, etc. (not quizId, ageBand, options)
- Biggest mismatches: naming drift (quizId vs id, options vs choices), extra fields in JSON not used by runtime
- Python pipeline should target emitting files matching the schema in packages/shared_types/src/schemas/quizSchema.ts exactly, with correct field names and types.
