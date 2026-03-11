# Quiz Runtime Schema

- Must match TypeScript runtime exactly
- See QUIZ_FORMAT_SYNC.md and QUIZ_FORMAT_EXAMPLE.json

Fields:
- id
- title
- ageGroup
- sections
- rubricRefs (optional)

Section:
- id
- title
- questions

Question:
- id
- type
- prompt
- mediaRef (optional)
- choices (optional)
- answerKey (string or array)
- distractors (optional)
- rubricRef (optional)
- domain (optional)
