import typer

from reporting.cli.commands import config_command, kind, parse, project, send, show

app = typer.Typer(help="Parse file with day (days) of tasks and save to many systems")

app.command("parse")(parse.parse)
app.command("show")(show.show)
app.command("send")(send.send)
app.add_typer(config_command.app, name="config")
app.add_typer(kind.app, name="kind")
app.add_typer(project.app, name="project")
