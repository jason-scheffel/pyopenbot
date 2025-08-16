from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

@dataclass
class Character:
    character_name: str
    character_card: str  # System prompt
    platform: str  # terminal or discord
    
    llm_provider: str
    llm_model: str
    api_key: str  # even if loaded from file
    
    settings: Dict[str, Any]  # No defaults - must be specified
    
    memory_type: str
    
    # Track if API key came from file (for saving back correctly)
    _api_key_source: Optional[str] = None  # 'file' or 'direct'

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Character":
        if not config_path.exists():
            raise FileNotFoundError(f"Character config file {config_path} does not exist")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        llm_config = config.get("llm", {})
        memory_config = config.get("memory", {})
        
        api_key = None
        api_key_source = None
        
        if "api_key" in llm_config:
            api_key = llm_config["api_key"]
            api_key_source = "direct"
        elif "api_key_file" in llm_config:
            key_path = Path(llm_config["api_key_file"]).expanduser()
            if key_path.exists():
                with open(key_path, "r") as f:
                    api_key = f.read().strip()
                api_key_source = f"file:{llm_config['api_key_file']}"
        
        instance = cls(
            character_name=config.get("character_name", ""),
            character_card=config.get("character_card", ""),
            platform=config.get("platform", ""),
            llm_provider=llm_config.get("provider", ""),
            llm_model=llm_config.get("model", ""),
            api_key=api_key or "",
            settings=llm_config.get("settings", {}),
            memory_type=memory_config.get("type", "")
        )
        instance._api_key_source = api_key_source
        return instance

    def save_to_yaml(self, config_path: Path) -> None:
        config = {
            "character_name": self.character_name,
            "character_card": self.character_card,
            "platform": self.platform,
            "llm": {
                "provider": self.llm_provider,
                "model": self.llm_model,
                "settings": self.settings
            },
            "memory": {
                "type": self.memory_type
            }
        }
        
        # Save API key based on how it was originally provided
        if self._api_key_source and self._api_key_source.startswith("file:"):
            file_path = self._api_key_source[5:]  # Remove "file:" prefix
            config["llm"]["api_key_file"] = file_path
        else:
            config["llm"]["api_key"] = self.api_key

        with open(config_path, "w") as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
