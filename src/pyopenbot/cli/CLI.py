import typer
from pyopenbot.commands.run import Run
from pyopenbot.commands.init import Init
from pyopenbot.commands.check import Check

class CLI:
    def __init__(self):
        self.app: typer.Typer = typer.Typer(
            help="OpenBot CLI", no_args_is_help=True
        )

        self.app.command("run")(Run().run)
        self.app.command("init")(Init().run)
        self.app.command("check")(Check().run)

    def run(self) -> None:
        self.app()
