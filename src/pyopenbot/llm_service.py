from any_llm import completion
from typing import List, Dict, Any, Optional
import requests
import asyncio
import time


class LLMService:
    def __init__(self, character):
        self.character = character
        self.model = f"openrouter/{character.llm_model}"  # e.g., "openrouter/z-ai/glm-4.5"
        
    async def get_response(self, user_message, conversation_history: List[Dict]) -> tuple[str, dict]:
        if isinstance(user_message, str):
            messages = [
                {"role": "system", "content": self.character.character_card},
                *conversation_history
            ]
        else:
            messages = [
                {"role": "system", "content": self.character.character_card},
                *conversation_history[:-1],
                {"role": "user", "content": user_message}
            ]
        
        completion_kwargs = {
            "model": self.model,
            "messages": messages,
            "api_key": self.character.api_key,
            "temperature": self.character.settings["temperature"],
            "top_p": self.character.settings.get("top_p", 0.9),
            "max_tokens": self.character.settings["max_tokens"],
            "presence_penalty": self.character.settings.get("presence_penalty", 0.0),
            "frequency_penalty": self.character.settings.get("frequency_penalty", 0.0),
        }
        
        if self.character.settings.get("reasoning_effort"):
            completion_kwargs["reasoning_effort"] = self.character.settings["reasoning_effort"]
        
        response = completion(**completion_kwargs)
        
        usage = {}
        
        if hasattr(response, 'id'):
            generation_id = response.id
            await asyncio.sleep(2)
            
            for attempt in range(3):
                try:
                    if attempt > 0:
                        await asyncio.sleep(1)
                    
                    headers = {'Authorization': f'Bearer {self.character.api_key}'}
                    gen_response = requests.get(
                        f'https://openrouter.ai/api/v1/generation?id={generation_id}',
                        headers=headers,
                        timeout=5
                    )
                    
                    if gen_response.status_code == 200:
                        gen_data = gen_response.json().get('data', {})
                        usage['cost'] = gen_data.get('total_cost', 0)
                        if gen_data.get('native_tokens_prompt'):
                            usage['prompt_tokens'] = gen_data.get('native_tokens_prompt', 0)
                        if gen_data.get('native_tokens_completion'):
                            usage['completion_tokens'] = gen_data.get('native_tokens_completion', 0)
                        usage['total_tokens'] = usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0)
                        break
                    elif gen_response.status_code == 404 and attempt < 2:
                        continue
                    else:
                        break
                except:
                    if attempt == 2:
                        break
                
        return response.choices[0].message.content, usage