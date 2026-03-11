
# Quiz Pipeline Workflow

## Attempt Summarisation & Prompt Generation

1. Export quiz attempt results as JSON (see examples/sample_attempt_export.json)
2. Run CLI command:
	```powershell
	python -m quiz_pipeline.cli.main summarise-child --child <id> --input <file> --quiz <quiz_json>
	```
3. The command outputs:
	- Readable summary of domain performance
	- JSON summary
	- LLM-ready prompt block

## Steps
1. Summarise child performance
2. Build LLM prompt
3. Validate quiz
4. Generate media
5. Build package

Each step is a CLI command.
