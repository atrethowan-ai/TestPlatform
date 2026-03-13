import typer
from quiz_pipeline.cli.commands import summarise_child, build_prompt, validate_quiz, generate_media, build_package, run_local_service

app = typer.Typer()


app.command(name="summarise-child")(summarise_child.main)
app.command(name="build-prompt")(build_prompt.main)
app.command(name="validate-quiz")(validate_quiz.main)
app.command(name="generate-media")(generate_media.main)
app.command(name="build-package")(build_package.main)
app.command(name="run-local-service")(run_local_service.main)

if __name__ == "__main__":
    app()
