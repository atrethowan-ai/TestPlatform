
import typer
import json
from quiz_pipeline.extract.attempt_loader import load_attempts
from quiz_pipeline.extract.attempt_summariser import summarise_attempts
from quiz_pipeline.prompts.prompt_builder import build_prompt

def main(child: str = typer.Option(..., '--child', help='Child ID'), input: str = typer.Option(..., '--input', help='Attempt export JSON'), quiz: str = typer.Option(None, '--quiz', help='Quiz JSON')):
    """Summarise child performance and generate LLM prompt."""
    attempt = load_attempts(input)
    if quiz:
        with open(quiz, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
    else:
        # Try to infer quiz file from attempt
        quiz_data = None
    if not quiz_data:
        print("Quiz JSON required for domain mapping.")
        return
    summary = summarise_attempts(attempt, quiz_data)
    print("\n=== Readable Summary ===")
    for domain, stats in summary['domainStats'].items():
        print(f"Domain: {domain} | Correct: {stats['correct']} | Incorrect: {stats['incorrect']} | Total: {stats['total']}")
    print("\nWeak Domains:", ', '.join(summary['weakDomains']) or 'None')
    print("\n=== JSON Summary ===")
    print(json.dumps(summary, indent=2))
    print("\n=== LLM Prompt ===")
    print(build_prompt(summary))
