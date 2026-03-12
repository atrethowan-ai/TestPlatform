# Quiz Authoring Schema

## Purpose
The authoring schema defines the canonical format for creating quizzes, whether by humans, LLMs (e.g., ChatGPT), or automated tools. It is the contract for all quiz content before transformation into runtime format.

## Authoring vs Runtime Schema
- **Authoring schema**: Rich, flexible, includes helper fields (e.g., audioText, ttsStyle, imageSpec, authoring metadata).
- **Runtime schema**: Minimal, only fields required for quiz delivery. Authoring-only fields are removed or transformed by the pipeline.

## Root Structure
```
Quiz (object):
	id: string (required)
	title: string (required)
	ageGroup: string (required)
	description: string (optional)
	sections: Section[] (required)
	rubricRefs: string[] (optional)
	estimatedDurationMinutes: int (optional)
```

## Section Structure
```
Section (object):
	id: string (required)
	title: string (required)
	questions: Question[] (required)
```

## Question Structure (Common Fields)
```
Question (object):
	id: string (required)
	type: string (required)
	prompt: string (required)
	answerKey: string | string[] (optional, required for most types)
	domain: string (optional)
	mediaRef: string (optional, pipeline-generated)
	choices: string[] (optional, for multiple_choice)
	distractors: string[] (optional, for multiple_choice)
	rubricRef: string (optional, for paragraph)
	audioText: string (optional, for audio_short_answer)
	ttsStyle: string (optional, for audio_short_answer)
	imageSpec: string (optional, for future image support)
```

## Required vs Optional Fields
- **Required**: id, type, prompt (all questions); choices (multiple_choice); answerKey (all except paragraph)
- **Optional**: domain, distractors, rubricRef, audioText, ttsStyle, imageSpec, mediaRef (pipeline-generated)

## Helper Fields (Authoring Only)
- audioText, ttsStyle, imageSpec: Used for media generation, not present in runtime
- mediaRef: Populated by pipeline after TTS/image generation

## Question Type Examples
### multiple_choice
```
{
	"id": "q1",
	"type": "multiple_choice",
	"prompt": "What is 2 + 2?",
	"choices": ["3", "4", "5"],
	"answerKey": "4",
	"domain": "arithmetic"
}
```
### short_answer
```
{
	"id": "q2",
	"type": "short_answer",
	"prompt": "What is the capital of France?",
	"answerKey": "Paris"
}
```
### paragraph
```
{
	"id": "q3",
	"type": "paragraph",
	"prompt": "Explain why the sky is blue.",
	"rubricRef": "writing_rubric_age9_v1"
}
```
### audio_short_answer
```
{
	"id": "q4",
	"type": "audio_short_answer",
	"prompt": "Spell the word 'elephant' after listening to the audio.",
	"answerKey": "elephant",
	"audioText": "Please spell the word: elephant.",
	"ttsStyle": "neutral"
}
```

## Pipeline Interpretation
- The pipeline validates all required fields.
- Helper fields are used for media generation and then removed.
- Only runtime-required fields are published to the TS system.
