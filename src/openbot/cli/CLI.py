import typer
from .cli_commands.Run import Run
from .cli_commands.Init import Init
from .cli_commands.Check import Check

class CLI:
    def __init__(self):
        self.app: typer.Typer = typer.Typer(
            help="OpenBot CLI", no_args_is_help=True
        )

        self.app.command("run")(Run().run_command)
        self.app.command("init")(Init().run_command)
        self.app.command("check")(Check().run_command)

    def run(self) -> None:
        self.app()