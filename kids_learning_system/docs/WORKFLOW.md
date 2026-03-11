# Workflow

1. Author quiz JSON and rubrics in content/
2. Validate with tools/quiz_builder
3. Add media assets to content/media/
4. Run the quiz shell (apps/quiz_shell)
5. Quiz attempts and results are stored in IndexedDB
6. Use CLI tools for export, analysis, and TTS media

# Development
- Use npm workspaces for dependency management
- Use Vitest for tests
- Use ESLint and Prettier for code quality
