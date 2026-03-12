
## Unified Local Server

A single Python FastAPI backend now:
- Serves the built quiz frontend UI (from `apps/quiz_shell/dist/`)
- Handles all API endpoints under `/api`
- Stores quiz attempts to disk
- Forms the foundation for a future LAN/local server

**How to run everything:**
1. Build the frontend:
   ```
   cd kids_learning_system/apps/quiz_shell
   npm install
   npm run build
   ```
2. Activate your Python environment
3. Install FastAPI and uvicorn if needed:
   ```
   pip install fastapi uvicorn pydantic
   ```
4. Run the service:
   ```
   python -m quiz_pipeline.cli.commands.run_local_service
   ```
5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

**API Endpoints:**
- `GET /api/health` — health check
- `POST /api/attempts` — save attempt JSON to disk
- `GET /api/attempts/{child_id}` — list attempts for a child

**Files saved:**
- `quiz_pipeline/work/attempts/<childId>/<completedAt>__<quizId>__<attemptId>.json`

See `docs/LOCAL_SERVICE.md` for full details and payload examples.
# Python Quiz Pipeline

This pipeline provides authoring, analysis, and media-generation tools for quizzes used in the kids_learning_system TypeScript runtime.


## Quickstart

1. Create a virtual environment:
   ```powershell
   cd quiz_pipeline
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run CLI:
   ```powershell
   python -m quiz_pipeline.cli.main
   ```

## GUI

To launch the GUI for summarising child performance, use the launcher script:

```powershell
python gui_app.py
```


## New GUI Workflow (2026)

The GUI now provides a child- and attempt-oriented workflow:

1. **Select Child**: Choose from a dropdown of known children (Forrest, Homie, Test User).
2. **Select Attempt**: After selecting a child, pick from a list of available attempts for that child (with quiz, timestamp, and attempt id).
3. **Automatic Quiz Resolution**: The app automatically finds the correct quiz file for the selected attempt.
4. **Generate Summary**: Click to generate a readable summary and LLM prompt.
5. **Copy Results**: Copy the full output to clipboard with one click.

### Advanced / Manual Mode
If needed, expand the "Advanced" section to manually select attempt and quiz files. This is only for troubleshooting or special cases.

### How Discovery Works
- **Children**: The dropdown is populated from a static list (Forrest, Homie, Test User). This can be extended in the future.
- **Attempts**: The app scans `work/generated/` for attempt JSONs and filters by selected child.
- **Quiz Resolution**: The app matches the `quizId` in the attempt to quiz files in `content/quizzes/age6/` and `content/quizzes/age9/`.

### Typical Workflow
1. Export attempts to `work/generated/` (or place them there).
2. Launch the GUI: `python gui_app.py`
3. Select child and attempt, click Generate Summary.
4. Copy results as needed.

See also: docs/WORKFLOW.md for more details.

## Architecture

- **Runtime schema**: Matches the TypeScript app (see docs/QUIZ_RUNTIME_SCHEMA.md)
- **Authoring schema**: Richer, allows helper fields (see docs/QUIZ_AUTHORING_SCHEMA.md)
- **Workflow**: Authoring → Normalize → Transform → Package

See docs/ARCHITECTURE.md for details.
