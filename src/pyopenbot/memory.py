from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Memory:
    type: str  # "unlimited" for now
    messages: List[Dict] = field(default_factory=list)
    max_context: int = 8192
    total_cost: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def add_usage(self, usage: dict):
        self.total_cost += usage.get('cost', 0.0)
        self.total_prompt_tokens += usage.get('prompt_tokens', 0)
        self.total_completion_tokens += usage.get('completion_tokens', 0)
    
    def clear(self):
        self.messages = []
        self.total_cost = 0.0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
    
    def get_messages(self) -> List[Dict]:
        return self.messages
    
    def get_stats(self) -> Dict[str, Any]:
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        
        return {
            "message_count": len(self.messages),
            "total_cost": self.total_cost,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": total_tokens,
            "context_usage": f"{total_tokens}/{self.max_context}",
            "context_percentage": (total_tokens / self.max_context) * 100 if self.max_context > 0 else 0
        }