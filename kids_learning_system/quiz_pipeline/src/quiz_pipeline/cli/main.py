import typer
from quiz_pipeline.cli.commands import summarise_child, build_prompt, validate_quiz, generate_media, build_package, run_local_service

app = typer.Typer()


app.command()(summarise_child.main)
app.command()(build_prompt.main)
app.command()(validate_quiz.main)
app.command()(generate_media.main)
app.command()(build_package.main)
app.command(name="run-local-service")(run_local_service.main)

if __name__ == "__main__":
    app()
