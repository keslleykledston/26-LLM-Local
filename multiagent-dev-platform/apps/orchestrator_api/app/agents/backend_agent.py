"""
Backend Developer Agent
Specialized in: Python, FastAPI, APIs, business logic
"""
from typing import Dict, Any
from loguru import logger

from app.agents.base import BaseAgent, AgentFactory


class BackendAgent(BaseAgent):
    """Backend development specialist"""

    def __init__(self):
        super().__init__()
        self.agent_type = "backend"
        self.agent_name = "Backend Developer"

    def get_system_prompt(self) -> str:
        return """You are an expert backend developer specializing in Python and API development.

EXPERTISE:
- Python, FastAPI, async/await
- RESTful API design
- Database integration (SQL, ORM)
- Authentication, authorization
- Error handling, validation
- Performance, scalability

RESPONSIBILITIES:
- Implement business logic
- Design API endpoints
- Ensure data validation
- Write secure, efficient code
- Handle errors gracefully

OUTPUT FORMAT:
Provide clean Python code with type hints.
Follow FastAPI best practices.
Include Pydantic models for validation.
"""

    async def execute_task(self, task: Any) -> Dict[str, Any]:
        """Execute a backend development task"""
        try:
            logger.info(f"⚙️ Backend Agent executing: {task.title}")

            task_context = f"Task: {task.title}\nDescription: {task.description}"

            response = await self.generate_with_context(
                prompt=f"Implement this backend task:\n\n{task.description}",
                task_context=task_context,
                temperature=0.3,
            )

            logger.success(f"✅ Backend task completed: {task.title}")

            return {
                "status": "completed",
                "implementation": response,
                "agent": self.agent_type,
            }

        except Exception as e:
            logger.error(f"❌ Backend agent failed: {e}")
            raise


# Register agent
AgentFactory.register_agent("backend", BackendAgent)
