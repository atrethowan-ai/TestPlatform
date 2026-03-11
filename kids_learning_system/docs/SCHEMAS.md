# Schemas

All content and data models are defined as Zod schemas and TypeScript interfaces in packages/shared_types.

## Quiz
- id, title, ageGroup, sections, rubricRefs
- Section: id, title, questions
- Question: id, type, prompt, mediaRef, choices, answerKey, distractors, rubricRef

## Rubric
- id, title, criteria (with levels and scores)

## AnalysisArtifact
- id, childId, quizId, createdAt, summary, weaknesses, recommendations

## InstructionSet
- id, childId, analysisId, createdAt, instructions

See packages/shared_types/src/schemas/ for full details.
