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
    
    discord_token: Optional[str] = None
    discord_channel_id: Optional[str] = None  # Channel ID to respond in
    
    _api_key_source: Optional[str] = None  # 'file' or 'direct'
    _discord_token_source: Optional[str] = None  # 'file' or 'direct'

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Character":
        if not config_path.exists():
            raise FileNotFoundError(f"Character config file {config_path} does not exist")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        llm_config = config.get("llm", {})
        memory_config = config.get("memory", {})
        discord_config = config.get("discord", {})
        
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
        
        discord_token = None
        discord_token_source = None
        discord_channel_id = None
        
        if config.get("platform") == "discord":
            if "token" in discord_config:
                discord_token = discord_config["token"]
                discord_token_source = "direct"
            elif "token_file" in discord_config:
                token_path = Path(discord_config["token_file"]).expanduser()
                if token_path.exists():
                    with open(token_path, "r") as f:
                        discord_token = f.read().strip()
                    discord_token_source = f"file:{discord_config['token_file']}"
            
            discord_channel_id = discord_config.get("channel_id")
        
        instance = cls(
            character_name=config.get("character_name", ""),
            character_card=config.get("character_card", ""),
            platform=config.get("platform", ""),
            llm_provider=llm_config.get("provider", ""),
            llm_model=llm_config.get("model", ""),
            api_key=api_key or "",
            settings=llm_config.get("settings", {}),
            memory_type=memory_config.get("type", ""),
            discord_token=discord_token,
            discord_channel_id=discord_channel_id
        )
        instance._api_key_source = api_key_source
        instance._discord_token_source = discord_token_source
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
        
        if self._api_key_source and self._api_key_source.startswith("file:"):
            file_path = self._api_key_source[5:]  # Remove "file:" prefix
            config["llm"]["api_key_file"] = file_path
        else:
            config["llm"]["api_key"] = self.api_key
        
        if self.platform == "discord" and self._discord_token_source:
            config["discord"] = {}
            if self._discord_token_source.startswith("file:"):
                file_path = self._discord_token_source[5:]  # Remove "file:" prefix
                config["discord"]["token_file"] = file_path
            else:
                config["discord"]["token"] = self.discord_token
            
            if self.discord_channel_id:
                config["discord"]["channel_id"] = self.discord_channel_id

        with open(config_path, "w") as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
