import typer
from .cli_commands.Run import Run
from .cli_commands.Test import Test


class CLI:
    def __init__(self):
        self.app: typer.Typer = typer.Typer(
            help="OpenBot CLI", no_args_is_help=True
        )

        self.app.command("run")(Run().run_command)
        self.app.command("test")(Test().run_command)

    def run(self) -> None:
        self.app()
