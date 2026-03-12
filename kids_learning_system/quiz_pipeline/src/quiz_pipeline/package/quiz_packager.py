
import logging
from quiz_pipeline.transform.authoring_to_runtime import transform_authoring_to_runtime
from quiz_pipeline.package.output_writer import write_output
import os
import json
from pathlib import Path

def package_quiz(authoring_quiz: dict, output_dir: str = "runtime_output", media_root: Path = None) -> dict:
    """
    Package an authoring quiz: validate, process, generate media, write runtime quiz JSON.
    media_root: optional base path for media files (MP3s). Defaults to output_dir.
    """
    logging.info("Validating authoring quiz")
    resolved_media_root = Path(media_root) if media_root else Path(output_dir)
    runtime_quiz = transform_authoring_to_runtime(authoring_quiz, media_root=resolved_media_root)
    quiz_id = runtime_quiz['id']
    out_dir = os.path.join(output_dir, quiz_id)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{quiz_id}_runtime.json")
    logging.info(f"Writing runtime quiz JSON to {out_path}")
    write_output(runtime_quiz, out_path)
    return runtime_quiz
