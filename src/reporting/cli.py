import typer

from reporting.commands import kind, parse, project, send, show

app = typer.Typer(help="Parse file with day (days) of tasks and save to many systems")

app.command("parse")(parse.parse)
app.command("show")(show.show)
app.command("send")(send.send)
app.add_typer(kind.app, name="kind")
app.add_typer(project.app, name="project")


def main(cli_args: list[str] | None = None) -> None:
    app(args=cli_args, standalone_mode=False)


if __name__ == "__main__":
    main()
