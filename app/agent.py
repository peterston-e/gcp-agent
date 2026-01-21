from typing import Optional, Dict
import asyncio

class SimpleAgent:
    """
    A simple agent that can be expanded with tools, memory, and LLM integration.
    This is your starting point - build upon this!
    """
    
    def __init__(self):
        self.name = "SimpleAgent"
        self.version = "1.0.0"
    
    async def process(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process incoming messages. 
        TODO: Add your agent logic here (LLM calls, tool use, etc.)
        """
        # Placeholder logic - replace with your agent implementation
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return f"Hello! I'm {self.name} v{self.version}. How can I help you today?"
        
        elif "weather" in message_lower:
            # This is where you'd integrate a weather API/tool
            return "Weather tool integration coming soon! This is your agent placeholder."
        
        elif "help" in message_lower:
            return ("I'm a simple agent MVP. You can:\n"
                   "- Greet me\n"
                   "- Ask about weather (placeholder)\n"
                   "- Extend my capabilities by modifying agent.py")
        
        else:
            return f"You said: '{message}'. I'm a basic agent - extend my capabilities in agent.py!"
    
    def add_tool(self, tool_name: str, tool_function):
        """Future: Add tools to your agent"""
        pass
    
    def set_memory(self, memory_backend):
        """Future: Add memory/context management"""
        pass