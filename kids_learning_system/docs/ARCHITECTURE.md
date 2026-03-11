# Monorepo Architecture

- **apps/quiz_shell**: Vite-based runtime app for children
- **packages/shared_types**: Central Zod schemas and TypeScript types
- **packages/quiz_domain**: Domain logic (scoring, validation, etc.)
- **packages/storage_indexeddb**: IndexedDB persistence layer
- **tools/quiz_builder**: CLI for quiz content validation/building
- **tools/tts_media_builder**: CLI for TTS audio asset management
- **content/**: Quizzes, media, rubrics, prompt templates
- **docs/**: Architecture, schema, workflow, storage, content docs
- **tests/**: Vitest-based tests for all layers

# Runtime vs Tooling Separation

- **Runtime (apps/quiz_shell)**: Loads quizzes, runs sessions, stores attempts, analyzes results. No direct access to tooling modules.
- **Tooling (tools/)**: CLI tools for validating/building content and media. No browser APIs.

# Zod Schema Validation

- All quiz, rubric, analysis, and instruction content is validated using Zod schemas in packages/shared_types.
- CLI tools and runtime both use these schemas for type safety and validation.

# IndexedDB Storage

- All persistent data (quizzes, attempts, profiles, analyses, instructions, media catalog, settings) is stored in IndexedDB via packages/storage_indexeddb.
- UI never accesses IndexedDB directly; always uses repository classes.

# Content Package Workflow

- Quizzes, rubrics, and prompt templates are stored in content/.
- Use tools/quiz_builder to validate and normalize quiz packages before use.
- Media assets referenced by quizzes are stored in content/media/.

# Upgrade Path to PWA

- The runtime app is Vite-based and can be upgraded to a PWA by adding a manifest, service worker, and offline support.
- All data is local-first and ready for offline use.
