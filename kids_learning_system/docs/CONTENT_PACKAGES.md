# Content Packages

- Quizzes are JSON files in content/quizzes/
- Rubrics are JSON files in content/rubrics/
- Prompt templates are Markdown in content/prompt_templates/
- Media assets are in content/media/

## Supported Question Types
- multiple_choice (with distractors, playful options)
- short_answer
- paragraph (manual review required)
- audio_short_answer (with mediaRef, answerKey)

All content is validated by Zod schemas in shared_types.
