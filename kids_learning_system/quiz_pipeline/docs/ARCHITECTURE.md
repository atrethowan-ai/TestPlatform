# Quiz Pipeline Architecture

## TypeScript Runtime
- Loads runtime quiz JSON (see QUIZ_FORMAT_SYNC.md)
- Validates and renders quizzes

## Python Pipeline
- Authoring, analysis, media generation
- Authoring schema (richer, helper fields)
- Normalization and transformation to runtime schema
- CLI for workflow automation

## Workflow
1. Authoring (LLM or manual)
2. Normalize/validate
3. Transform to runtime
4. Generate media
5. Package for TS runtime
