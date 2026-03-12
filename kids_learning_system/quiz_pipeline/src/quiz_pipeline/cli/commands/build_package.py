
import typer
import logging
import json
from pathlib import Path
from quiz_pipeline.package.quiz_packager import package_quiz

def main(
    input: str = typer.Option(..., help="Path to authoring quiz JSON")
):
    """
    Build/package a quiz: validates, processes, generates media, writes runtime JSON.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        logging.info(f"Loading authoring quiz from {input}")
        with open(input, "r", encoding="utf-8") as f:
            authoring_quiz = json.load(f)
        package_quiz(authoring_quiz)
        logging.info("Packaging complete.")
    except Exception as e:
        logging.error(f"Packaging failed: {e}")
        raise typer.Exit(code=1)
