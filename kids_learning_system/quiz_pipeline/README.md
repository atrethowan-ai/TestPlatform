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

The GUI allows you to:
- Enter Child ID
- Browse for attempt export JSON
- Browse for quiz JSON
- Generate summary and LLM prompt
- Copy output to clipboard

## Architecture

- **Runtime schema**: Matches the TypeScript app (see docs/QUIZ_RUNTIME_SCHEMA.md)
- **Authoring schema**: Richer, allows helper fields (see docs/QUIZ_AUTHORING_SCHEMA.md)
- **Workflow**: Authoring → Normalize → Transform → Package

See docs/ARCHITECTURE.md for details.
