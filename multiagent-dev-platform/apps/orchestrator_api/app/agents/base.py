"""
Base Agent class and factory
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from loguru import logger

from app.services.ollama_service import OllamaService
from app.services.memory_service import MemoryService
from app.tools.repo_tools import RepoTools


class BaseAgent(ABC):
    """Base class for all specialized agents"""

    def __init__(self):
        self.ollama = OllamaService()
        self.memory = MemoryService()
        self.repo_tools = RepoTools()
        self.agent_type: str = "base"
        self.agent_name: str = "Base Agent"

    @abstractmethod
    async def execute_task(self, task: Any) -> Dict[str, Any]:
        """Execute a task - must be implemented by subclasses"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get agent's system prompt"""
        pass

    async def query_memory(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Query long-term memory for relevant context"""
        return await self.memory.search(query=query, limit=limit)

    async def generate_with_context(
        self, prompt: str, task_context: str, temperature: float = 0.7
    ) -> str:
        """Generate response with memory context"""
        # Get relevant context from memory
        memory_results = await self.query_memory(prompt, limit=3)

        # Build context
        context_parts = []
        if memory_results:
            context_parts.append("RELEVANT KNOWLEDGE FROM MEMORY:")
            for item in memory_results:
                context_parts.append(f"- {item['title']}: {item['content'][:200]}...")

        context_parts.append(f"\nTASK CONTEXT:\n{task_context}")
        context_parts.append(f"\nPROMPT:\n{prompt}")

        full_prompt = "\n\n".join(context_parts)

        # Generate using Ollama
        response = await self.ollama.generate(
            prompt=full_prompt,
            system=self.get_system_prompt(),
            temperature=temperature,
        )

        return response


class AgentFactory:
    """Factory for creating specialized agents"""

    _agents = {}

    @classmethod
    def register_agent(cls, agent_type: str, agent_class):
        """Register an agent type"""
        cls._agents[agent_type] = agent_class

    @classmethod
    def create_agent(cls, agent_type: str) -> BaseAgent:
        """Create an agent by type"""
        agent_class = cls._agents.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")

        return agent_class()

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent types"""
        return list(cls._agents.keys())
