from any_llm import completion
from typing import List, Dict, Any, Optional


class LLMService:
    def __init__(self, character):
        self.character = character
        self.model = f"openrouter/{character.llm_model}"  # e.g., "openrouter/z-ai/glm-4.5"
        
    def get_response(self, user_message: str, conversation_history: List[Dict]) -> str:
        messages = [
            {"role": "system", "content": self.character.character_card},
            *conversation_history,
            {"role": "user", "content": user_message}
        ]
        
        response = completion(
            model=self.model,
            messages=messages,
            api_key=self.character.api_key,
            temperature=self.character.settings["temperature"],
            top_p=self.character.settings.get("top_p", 0.9),
            max_tokens=self.character.settings["max_tokens"],
            presence_penalty=self.character.settings.get("presence_penalty", 0.0),
            frequency_penalty=self.character.settings.get("frequency_penalty", 0.0),
        )
        
        return response.choices[0].message.content
    
    def count_tokens(self, messages: List[Dict]) -> int:
        total = 0
        for msg in messages:
            total += len(msg.get("content", "")) // 4  # Rough estimate: 1 token ≈ 4 chars
        return total