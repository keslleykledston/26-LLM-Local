"""
Database / Performance Specialist Agent
Specialized in: SQL, indexes, query optimization, data modeling
"""
from typing import Dict, Any
from loguru import logger

from app.agents.base import BaseAgent, AgentFactory


class DatabaseAgent(BaseAgent):
    """Database and performance specialist"""

    def __init__(self):
        super().__init__()
        self.agent_type = "database"
        self.agent_name = "Database / Performance Specialist"

    def get_system_prompt(self) -> str:
        return """You are an expert database engineer and performance specialist.

EXPERTISE:
- SQL, PostgreSQL optimization
- Database design, normalization
- Indexing strategies
- Query optimization
- Performance profiling
- Caching strategies

RESPONSIBILITIES:
- Design efficient schemas
- Optimize queries
- Create proper indexes
- Ensure data integrity
- Improve performance

OUTPUT FORMAT:
Provide SQL with explanatory comments.
Include performance considerations.
Suggest indexes where appropriate.
"""

    async def execute_task(self, task: Any) -> Dict[str, Any]:
        """Execute a database/performance task"""
        try:
            logger.info(f"🗄️ Database Agent executing: {task.title}")

            task_context = f"Task: {task.title}\nDescription: {task.description}"

            response = await self.generate_with_context(
                prompt=f"Implement this database/performance task:\n\n{task.description}",
                task_context=task_context,
                temperature=0.2,
            )

            logger.success(f"✅ Database task completed: {task.title}")

            return {
                "status": "completed",
                "implementation": response,
                "agent": self.agent_type,
            }

        except Exception as e:
            logger.error(f"❌ Database agent failed: {e}")
            raise


# Register agent
AgentFactory.register_agent("database", DatabaseAgent)
