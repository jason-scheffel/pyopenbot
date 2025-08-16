import pytest
from pathlib import Path
import tempfile
import yaml
from pyopenbot.character import Character


class TestCharacter:
    def test_load_valid_config(self):
        config_path = Path("tests/fixtures/valid_config.yaml")
        character = Character.from_yaml(config_path)
        
        assert character.character_name == "TestBot"
        assert "helpful test assistant" in character.character_card
        assert character.platform == "terminal"
        assert character.llm_provider == "openrouter"
        assert character.llm_model == "z-ai/glm-4.5"
        assert character.api_key == "test-api-key-123"
        assert character.settings["temperature"] == 0.7
        assert character.settings["max_tokens"] == 2000
        assert character.memory_type == "unlimited"
        assert character._api_key_source == "direct"
    
    def test_load_config_with_file_key(self):
        config_path = Path("tests/fixtures/config_with_file_key.yaml")
        character = Character.from_yaml(config_path)
        
        assert character.character_name == "TestBotFile"
        assert character.platform == "discord"
        assert character.api_key == "test-key-from-file-789"
        assert character._api_key_source == "file:tests/fixtures/test_api_key.txt"
    
    def test_load_invalid_config_missing_fields(self):
        config_path = Path("tests/fixtures/invalid_config.yaml")
        character = Character.from_yaml(config_path)
        
        assert character.character_name == "InvalidBot"
        assert character.character_card == ""  # Missing field returns empty
        assert character.platform == "invalid_platform"
        assert character.llm_model == ""  # Missing field returns empty
        assert character.api_key == ""  # Missing api_key returns empty
        assert character.memory_type == ""  # Missing memory returns empty
    
    def test_load_nonexistent_file(self):
        config_path = Path("tests/fixtures/nonexistent.yaml")
        
        with pytest.raises(FileNotFoundError):
            Character.from_yaml(config_path)
    
    def test_save_config_preserves_direct_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        character = Character(
            character_name="SaveTest",
            character_card="Test save",
            platform="terminal",
            llm_provider="openrouter",
            llm_model="z-ai/glm-4.5",
            api_key="direct-key",
            settings={"temperature": 0.5},
            memory_type="unlimited"
        )
        character._api_key_source = "direct"
        
        character.save_to_yaml(temp_path)
        
        with open(temp_path) as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["llm"]["api_key"] == "direct-key"
        assert "api_key_file" not in saved_config["llm"]
        
        temp_path.unlink()
    
    def test_save_config_preserves_file_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        character = Character(
            character_name="SaveTest",
            character_card="Test save",
            platform="terminal",
            llm_provider="openrouter",
            llm_model="z-ai/glm-4.5",
            api_key="actual-key-value",
            settings={"temperature": 0.5},
            memory_type="unlimited"
        )
        character._api_key_source = "file:path/to/key.txt"
        
        character.save_to_yaml(temp_path)
        
        with open(temp_path) as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["llm"]["api_key_file"] == "path/to/key.txt"
        assert "api_key" not in saved_config["llm"]
        
        temp_path.unlink()