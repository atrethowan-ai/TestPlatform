
import typer
import logging
import json
import os
import shutil
from pathlib import Path
from quiz_pipeline.package.quiz_packager import package_quiz


def _resolve_input_path(raw_input: str, quiz_pipeline_root: Path) -> Path:
    input_path = Path(raw_input)
    if input_path.is_absolute() and input_path.exists():
        return input_path

    cwd_candidate = (Path.cwd() / input_path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    repo_candidate = (quiz_pipeline_root / input_path).resolve()
    if repo_candidate.exists():
        return repo_candidate

    raise FileNotFoundError(f"Input quiz JSON not found: {raw_input}")


def _publish_runtime_quiz_and_media(runtime_quiz: dict, generated_dir: Path, public_dir: Path, dist_dir: Path) -> None:
    quiz_id = runtime_quiz["id"]
    runtime_json = generated_dir / quiz_id / f"{quiz_id}_runtime.json"
    if not runtime_json.exists():
        raise FileNotFoundError(f"Runtime JSON not found after packaging: {runtime_json}")

    public_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    public_quiz_json = public_dir / f"{quiz_id}.json"
    dist_quiz_json = dist_dir / f"{quiz_id}.json"
    shutil.copy2(runtime_json, public_quiz_json)
    shutil.copy2(runtime_json, dist_quiz_json)
    logging.info(f"Published quiz JSON -> {public_quiz_json}")
    logging.info(f"Published quiz JSON -> {dist_quiz_json}")

    generated_media_dir = generated_dir / "media" / "spelling" / quiz_id
    if generated_media_dir.exists():
        public_media_dir = public_dir / "media" / "spelling" / quiz_id
        dist_media_dir = dist_dir / "media" / "spelling" / quiz_id
        public_media_dir.mkdir(parents=True, exist_ok=True)
        dist_media_dir.mkdir(parents=True, exist_ok=True)
        for mp3 in generated_media_dir.glob("*.mp3"):
            shutil.copy2(mp3, public_media_dir / mp3.name)
            shutil.copy2(mp3, dist_media_dir / mp3.name)
        logging.info(f"Published media -> {public_media_dir}")
        logging.info(f"Published media -> {dist_media_dir}")


def _refresh_manifest(public_dir: Path, dist_dir: Path) -> None:
    manifest = []
    for quiz_file in sorted(public_dir.glob("*.json")):
        if quiz_file.name == "quiz_manifest.json":
            continue
        try:
            data = json.loads(quiz_file.read_text(encoding="utf-8"))
        except Exception:
            # Ignore non-JSON or invalid placeholders
            continue
        quiz_id = data.get("id") or data.get("quizId")
        if not quiz_id:
            continue
        manifest.append(
            {
                "id": quiz_id,
                "title": data.get("title", quiz_id),
                "ageGroup": data.get("ageGroup") or data.get("ageBand") or "all",
                "path": f"/{quiz_file.name}",
            }
        )

    public_manifest = public_dir / "quiz_manifest.json"
    dist_manifest = dist_dir / "quiz_manifest.json"
    public_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    dist_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logging.info(f"Updated manifest -> {public_manifest}")
    logging.info(f"Updated manifest -> {dist_manifest}")

def main(
    input: str = typer.Option(..., help="Path to authoring quiz JSON"),
    tts_cwd: str = typer.Option("", "--tts-cwd", help="Optional working directory for Kokoro config resolution."),
):
    """
    Build/package a quiz: validates, processes, generates media, writes runtime JSON.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        # .../kids_learning_system/quiz_pipeline
        quiz_pipeline_root = Path(__file__).resolve().parents[4]
        kids_system_root = quiz_pipeline_root.parent
        generated_dir = (quiz_pipeline_root / "work" / "generated").resolve()
        public_dir = (kids_system_root / "apps" / "quiz_shell" / "public").resolve()
        dist_dir = (kids_system_root / "apps" / "quiz_shell" / "dist").resolve()

        input_path = _resolve_input_path(input, quiz_pipeline_root)
        logging.info(f"Loading authoring quiz from {input_path}")
        with open(input_path, "r", encoding="utf-8") as f:
            authoring_quiz = json.load(f)

        configured_tts_cwd = tts_cwd.strip()
        if not configured_tts_cwd:
            env_tts_root = os.environ.get("VOICE_AGENT_ROOT", "").strip()
            default_tts_root = "C:/DEV/260305_ComplexVoiceAgent"
            configured_tts_cwd = env_tts_root or default_tts_root

        original_cwd = Path.cwd()
        tts_working_dir = Path(configured_tts_cwd)
        if configured_tts_cwd and tts_working_dir.exists():
            os.chdir(tts_working_dir)
            logging.info(f"Using TTS working directory: {tts_working_dir}")

        try:
            runtime_quiz = package_quiz(
                authoring_quiz,
                output_dir=str(generated_dir),
                media_root=generated_dir,
            )
        finally:
            os.chdir(original_cwd)

        _publish_runtime_quiz_and_media(runtime_quiz, generated_dir, public_dir, dist_dir)
        _refresh_manifest(public_dir, dist_dir)
        logging.info("Packaging and publishing complete.")
    except Exception as e:
        logging.error(f"Packaging failed: {e}")
        raise typer.Exit(code=1)
