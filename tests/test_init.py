import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import yaml
from pyopenbot.commands.init import Init
from pyopenbot.character import Character


class TestInitCommand:
    def test_init_with_direct_api_key(self):
        init = Init()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        mock_inputs = {
            "Character name": "TestBot",
            "Select platform": "terminal",
            "Select model": "z-ai/glm-4.5",
            "Read API key from file?": False,
            "Enter OpenRouter API key": "test-api-123",
            "Temperature (0.0-2.0)": 0.7,
            "Top-p (0.0-1.0)": 0.9,
            "Max response tokens": 2000,
            "Context window size": 8192,
            "Memory type": "unlimited",
            "Save as": str(temp_path)
        }
        
        with patch('pyopenbot.commands.init.Prompt.ask') as mock_prompt, \
             patch('pyopenbot.commands.init.Confirm.ask') as mock_confirm, \
             patch('pyopenbot.commands.init.FloatPrompt.ask') as mock_float, \
             patch('pyopenbot.commands.init.IntPrompt.ask') as mock_int, \
             patch('builtins.input') as mock_input, \
             patch.object(init.console, 'print'):
            
            mock_prompt.side_effect = lambda prompt, **kwargs: (
                mock_inputs.get(prompt) or 
                (kwargs.get('default') if 'default' in kwargs else None)
            )
            mock_confirm.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, False)
            mock_float.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, 0.7)
            mock_int.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, 2000)
            mock_input.side_effect = ["Test system prompt", "", ""]
            
            init.run()
        
        assert temp_path.exists()
        
        character = Character.from_yaml(temp_path)
        assert character.character_name == "TestBot"
        assert character.character_card == "Test system prompt"
        assert character.platform == "terminal"
        assert character.llm_model == "z-ai/glm-4.5"
        assert character.api_key == "test-api-123"
        assert character.settings["temperature"] == 0.7
        assert character.memory_type == "unlimited"
        
        temp_path.unlink()
    
    def test_init_with_file_api_key(self):
        init = Init()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        mock_inputs = {
            "Character name": "TestBotFile",
            "Select platform": "discord",
            "Select model": "z-ai/glm-4.5",
            "Read API key from file?": True,
            "API key file path": "/path/to/key.txt",
            "Temperature (0.0-2.0)": 0.8,
            "Top-p (0.0-1.0)": 0.95,
            "Max response tokens": 1500,
            "Context window size": 4096,
            "Memory type": "unlimited",
            "Save as": str(temp_path)
        }
        
        with patch('pyopenbot.commands.init.Prompt.ask') as mock_prompt, \
             patch('pyopenbot.commands.init.Confirm.ask') as mock_confirm, \
             patch('pyopenbot.commands.init.FloatPrompt.ask') as mock_float, \
             patch('pyopenbot.commands.init.IntPrompt.ask') as mock_int, \
             patch('builtins.input') as mock_input, \
             patch.object(init.console, 'print'):
            
            mock_prompt.side_effect = lambda prompt, **kwargs: (
                mock_inputs.get(prompt) or 
                (kwargs.get('default') if 'default' in kwargs else None)
            )
            mock_confirm.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, False)
            mock_float.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, 0.8)
            mock_int.side_effect = lambda prompt, **kwargs: mock_inputs.get(prompt, 1500)
            mock_input.side_effect = ["Bot from file", "", ""]
            
            init.run()
        
        assert temp_path.exists()
        
        with open(temp_path) as f:
            config = yaml.safe_load(f)
        
        assert config["character_name"] == "TestBotFile"
        assert config["platform"] == "discord"
        assert config["llm"]["api_key_file"] == "/path/to/key.txt"
        assert "api_key" not in config["llm"]
        assert config["llm"]["settings"]["temperature"] == 0.8
        
        temp_path.unlink()
    
    def test_init_with_multiline_prompt(self):
        init = Init()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        with patch('pyopenbot.commands.init.Prompt.ask') as mock_prompt, \
             patch('pyopenbot.commands.init.Confirm.ask') as mock_confirm, \
             patch('pyopenbot.commands.init.FloatPrompt.ask') as mock_float, \
             patch('pyopenbot.commands.init.IntPrompt.ask') as mock_int, \
             patch('builtins.input') as mock_input, \
             patch.object(init.console, 'print'):
            
            mock_prompt.side_effect = lambda prompt, **kwargs: (
                "MultiLineBot" if "Character name" in prompt
                else "terminal" if "platform" in prompt
                else "z-ai/glm-4.5" if "model" in prompt
                else "test-key" if "API key" in prompt
                else "unlimited" if "Memory" in prompt
                else str(temp_path) if "Save as" in prompt
                else kwargs.get('default')
            )
            mock_confirm.return_value = False
            mock_float.return_value = 0.7
            mock_int.return_value = 2000
            
            mock_input.side_effect = [
                "You are a helpful assistant.",
                "Be friendly and concise.",
                "Always be respectful.",
                "",
                ""
            ]
            
            init.run()
        
        character = Character.from_yaml(temp_path)
        expected_prompt = "You are a helpful assistant.\nBe friendly and concise.\nAlways be respectful."
        assert character.character_card == expected_prompt
        
        temp_path.unlink()
    
    def test_init_with_defaults(self):
        init = Init()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        with patch('pyopenbot.commands.init.Prompt.ask') as mock_prompt, \
             patch('pyopenbot.commands.init.Confirm.ask') as mock_confirm, \
             patch('pyopenbot.commands.init.FloatPrompt.ask') as mock_float, \
             patch('pyopenbot.commands.init.IntPrompt.ask') as mock_int, \
             patch('builtins.input') as mock_input, \
             patch.object(init.console, 'print'):
            
            # Use all defaults
            mock_prompt.side_effect = lambda prompt, **kwargs: (
                str(temp_path) if "Save as" in prompt
                else kwargs.get('default', kwargs.get('choices', [None])[0] if 'choices' in kwargs else None)
            )
            mock_confirm.side_effect = lambda prompt, **kwargs: kwargs.get('default', False)
            mock_float.side_effect = lambda prompt, **kwargs: kwargs.get('default', 0.7)
            mock_int.side_effect = lambda prompt, **kwargs: kwargs.get('default', 2000)
            mock_input.side_effect = ["", ""]  # Empty prompt
            
            init.run()
        
        character = Character.from_yaml(temp_path)
        assert character.character_name == "Assistant"
        assert character.character_card == "You are a helpful AI assistant. Be concise and friendly."
        assert character.platform == "terminal"
        assert character.llm_model == "z-ai/glm-4.5"
        assert character.settings["temperature"] == 0.7
        assert character.settings["top_p"] == 0.9
        assert character.settings["max_tokens"] == 2000
        assert character.settings["context_window"] == 8192
        
        temp_path.unlink()