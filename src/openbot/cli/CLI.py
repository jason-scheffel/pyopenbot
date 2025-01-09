import typer
from openbot.commands.run import Run
from openbot.commands.init import Init
from openbot.commands.check import Check
from openbot.platforms.cli_platform import CLIPlatform

class CLI:
    def __init__(self):
        self.app: typer.Typer = typer.Typer(
            help="OpenBot CLI", no_args_is_help=True
        )

        self.platform = CLIPlatform()

        self.app.command("run")(Run(self.platform).run)
        self.app.command("init")(Init(self.platform).run)
        self.app.command("check")(Check(self.platform).run)

    def run(self) -> None:
        self.app()
