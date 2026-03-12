
# Quiz Pipeline Workflow


## Attempt Summarisation & Prompt Generation

### New GUI Workflow (2026)

1. Export quiz attempt results as JSON (see examples/sample_attempt_export.json) to `work/generated/`.
2. Launch the GUI: `python gui_app.py`
3. Select a child from the dropdown.
4. Select an attempt for that child (shows quiz, timestamp, attempt id).
5. The GUI automatically resolves the correct quiz file for the attempt.
6. Click Generate Summary to view results and LLM prompt.
7. Copy results to clipboard as needed.

#### Advanced/Manual Mode
Expand the "Advanced" section to manually select attempt and quiz files if needed.

#### How Discovery Works
- **Children**: Static list (Forrest, Homie, Test User)
- **Attempts**: Scans `work/generated/` for attempt JSONs, filters by child
- **Quiz Resolution**: Matches `quizId` in attempt to quiz files in `content/quizzes/age6/` and `content/quizzes/age9/`

## Steps
1. Summarise child performance
2. Build LLM prompt
3. Validate quiz
4. Generate media
5. Build package

Each step is a CLI command.
