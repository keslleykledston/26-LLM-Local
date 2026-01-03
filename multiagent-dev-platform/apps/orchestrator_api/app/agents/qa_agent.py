"""
QA + UX Specialist Agent
Specialized in: Testing, validation, user experience, accessibility
"""
from typing import Dict, Any
from loguru import logger

from app.agents.base import BaseAgent, AgentFactory


class QAAgent(BaseAgent):
    """QA and UX specialist"""

    def __init__(self):
        super().__init__()
        self.agent_type = "qa"
        self.agent_name = "QA + UX Specialist"

    def get_system_prompt(self) -> str:
        return """You are an expert QA engineer and UX specialist.

EXPERTISE:
- Test-driven development (TDD)
- Unit, integration, E2E tests
- User experience (UX) design
- Accessibility (WCAG, ARIA)
- Edge case identification
- Quality assurance

RESPONSIBILITIES:
- Write comprehensive tests
- Identify edge cases
- Ensure accessibility
- Validate UX flow
- Catch bugs early

OUTPUT FORMAT:
Provide test code with clear assertions.
Cover happy path and edge cases.
Include accessibility checks.
"""

    async def execute_task(self, task: Any) -> Dict[str, Any]:
        """Execute a QA/UX task"""
        try:
            logger.info(f"✅ QA Agent executing: {task.title}")

            task_context = f"Task: {task.title}\nDescription: {task.description}"

            response = await self.generate_with_context(
                prompt=f"Implement this QA/UX task:\n\n{task.description}",
                task_context=task_context,
                temperature=0.3,
            )

            logger.success(f"✅ QA task completed: {task.title}")

            return {
                "status": "completed",
                "implementation": response,
                "agent": self.agent_type,
            }

        except Exception as e:
            logger.error(f"❌ QA agent failed: {e}")
            raise


# Register agent
AgentFactory.register_agent("qa", QAAgent)
