from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Character:
    character_platform_name: str
    character_card: str
    text_llm: str
    text_llm_provider: str

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Character":
        if not config_path.exists():
            raise FileNotFoundError(f"Character config file {config_path} does not exist")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        if not all(key in config for key in ["character_platform_name", "character_card", "text_llm", "text_llm_provider"]):
            raise ValueError("Character config file is missing required fields")

        return cls(
            character_platform_name=config["character_platform_name"],
            character_card=config["character_card"],
            text_llm=config["text_llm"],
            text_llm_provider=config["text_llm_provider"]
        )

    def save_to_yaml(self, config_path: Path) -> None:
        config = {
            "character_platform_name": self.character_platform_name,
            "character_card": self.character_card,
            "text_llm": self.text_llm,
            "text_llm_provider": self.text_llm_provider
        }

        with open(config_path, "w") as file:
            yaml.dump(config, file)
