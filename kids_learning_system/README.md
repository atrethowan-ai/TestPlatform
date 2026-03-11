# kids_learning_system

A local-first educational quiz system for children, educators, and parents. Built as a TypeScript monorepo with clean separation of UI, domain, persistence, and tooling. Supports content packages, longitudinal skill tracking, and future PWA upgrade.

## Monorepo Structure

- **apps/quiz_shell**: Vite-based runtime app for children
- **packages/shared_types**: Central Zod schemas and TypeScript types
- **packages/quiz_domain**: Domain logic (scoring, validation, etc.)
- **packages/storage_indexeddb**: IndexedDB persistence layer
- **tools/quiz_builder**: CLI for quiz content validation/building
- **tools/tts_media_builder**: CLI for TTS audio asset management
- **content/**: Quizzes, media, rubrics, prompt templates
- **docs/**: Architecture, schema, workflow, storage, content docs
- **tests/**: Vitest-based tests for all layers

## Quick Start

1. `npm install`
2. `npm run dev --workspace=apps/quiz_shell`
3. Open http://localhost:5173

## Key Features
- Local-first, privacy-respecting
- Modular, extensible, PWA-ready
- Zod-validated content packages
- IndexedDB for all persistent data
- CLI tools for content and media

See docs/ for full architecture and workflow details.
