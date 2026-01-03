"""
Frontend Developer Agent
Specialized in: React, Next.js, TypeScript, CSS, UI/UX
"""
from typing import Dict, Any
from loguru import logger

from app.agents.base import BaseAgent, AgentFactory


class FrontendAgent(BaseAgent):
    """Frontend development specialist"""

    def __init__(self):
        super().__init__()
        self.agent_type = "frontend"
        self.agent_name = "Frontend Developer"

    def get_system_prompt(self) -> str:
        return """You are an expert frontend developer specializing in modern web development.

EXPERTISE:
- React, Next.js, TypeScript
- Tailwind CSS, responsive design
- Component architecture, hooks
- State management (Context, Zustand)
- Accessibility (a11y), SEO
- Performance optimization

RESPONSIBILITIES:
- Implement UI components
- Ensure responsive design
- Write clean, typed code
- Follow React best practices
- Consider UX and accessibility

OUTPUT FORMAT:
Provide clear, working code with proper TypeScript types.
Include comments for complex logic only.
"""

    async def execute_task(self, task: Any) -> Dict[str, Any]:
        """Execute a frontend development task"""
        try:
            logger.info(f"🎨 Frontend Agent executing: {task.title}")

            # Build task context
            task_context = f"Task: {task.title}\nDescription: {task.description}"

            # Generate implementation
            response = await self.generate_with_context(
                prompt=f"Implement this frontend task:\n\n{task.description}",
                task_context=task_context,
                temperature=0.3,
            )

            logger.success(f"✅ Frontend task completed: {task.title}")

            return {
                "status": "completed",
                "implementation": response,
                "agent": self.agent_type,
            }

        except Exception as e:
            logger.error(f"❌ Frontend agent failed: {e}")
            raise


# Register agent
AgentFactory.register_agent("frontend", FrontendAgent)
