from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class PyOpenBotConfig:
    platform_name: str

    @classmethod
    def from_yaml(cls, config_path: Path) -> "PyOpenBotConfig":
        if not config_path.exists():
            raise FileNotFoundError(f"PyOpenBot config file {config_path} does not exist")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        if not all(key in config for key in ["platform_name"]):
            raise ValueError("Character config file is missing required fields")

        return cls(
            platform_name=config["platform_name"]
        )

    def save_to_yaml(self, config_path: Path) -> None:
        config = {
            "platform_name": self.platform_name
        }

        with open(config_path, "w") as file:
            yaml.dump(config, file)
