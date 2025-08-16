from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Memory:
    type: str  # "unlimited" for now
    messages: List[Dict] = field(default_factory=list)
    max_context: int = 8192
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def clear(self):
        self.messages = []
    
    def get_messages(self) -> List[Dict]:
        return self.messages
    
    def get_token_count(self) -> int:
        return sum(len(msg.get("content", "")) // 4 for msg in self.messages)
    
    def get_stats(self) -> Dict[str, Any]:
        token_count = self.get_token_count()
        return {
            "message_count": len(self.messages),
            "token_count": token_count,
            "context_usage": f"{token_count}/{self.max_context}",
            "context_percentage": (token_count / self.max_context) * 100
        }