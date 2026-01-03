"""
Orchestrator - Main agent coordinator following the pipeline:
PLAN → EXECUTE → VALIDATE → INTEGRATE → MEMORY
"""
from loguru import logger
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import traceback

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.mission import Mission
from app.models.task import Task
from app.services.ollama_service import OllamaService
from app.services.memory_service import MemoryService
from app.services.external_ai_service import ExternalAIService
from app.agents.base import AgentFactory
from app.tools.repo_tools import RepoTools
from app.tools.git_tools import GitTools
from app.tools.runner_tools import RunnerTools
from sqlalchemy import select


class Orchestrator:
    """
    Main orchestrator that coordinates all agents through the pipeline
    """

    def __init__(self):
        self.ollama = OllamaService()
        self.memory = MemoryService()
        self.external_ai = ExternalAIService()
        self.repo_tools = RepoTools()
        self.git_tools = GitTools()
        self.runner_tools = RunnerTools()
        self.max_concurrent_tasks = 3  # Limit concurrent task execution
        self._cancelled_missions = set()  # Track cancelled missions

    async def cancel_mission(self, mission_id: int) -> None:
        """Cancel a running mission"""
        self._cancelled_missions.add(mission_id)
        logger.warning(f"⚠️ Mission #{mission_id} marked for cancellation")

    def _check_cancelled(self, mission_id: int) -> None:
        """Check if mission was cancelled and raise exception if so"""
        if mission_id in self._cancelled_missions:
            raise asyncio.CancelledError(f"Mission #{mission_id} was cancelled")

    async def execute_mission(self, mission_id: int) -> None:
        """
        Execute a mission through the complete pipeline
        """
        async with AsyncSessionLocal() as db:
            try:
                # Load mission
                result = await db.execute(select(Mission).where(Mission.id == mission_id))
                mission = result.scalar_one()

                logger.info(f"🎯 Starting mission #{mission_id}: {mission.title}")

                # ━━━ PHASE 1: PLAN ━━━
                self._check_cancelled(mission_id)
                logger.info("📋 PHASE 1: PLANNING")
                await self._update_mission_status(db, mission, "planning")
                plan = await self._phase_plan(db, mission)
                mission.plan = plan
                await db.commit()

                # ━━━ PHASE 2: EXECUTE ━━━
                self._check_cancelled(mission_id)
                logger.info("⚙️ PHASE 2: EXECUTION")
                await self._update_mission_status(db, mission, "executing")
                results = await self._phase_execute(db, mission, plan)

                # ━━━ PHASE 3: VALIDATE ━━━
                self._check_cancelled(mission_id)
                logger.info("✅ PHASE 3: VALIDATION")
                await self._update_mission_status(db, mission, "validating")
                validation_passed = await self._phase_validate(db, mission)

                if not validation_passed:
                    logger.error("❌ Validation failed - rejecting mission")
                    await self._update_mission_status(db, mission, "failed")
                    return

                # ━━━ PHASE 4: INTEGRATE ━━━
                self._check_cancelled(mission_id)
                logger.info("🔗 PHASE 4: INTEGRATION")
                await self._update_mission_status(db, mission, "integrating")
                await self._phase_integrate(db, mission)

                # ━━━ PHASE 5: MEMORY ━━━
                logger.info("🧠 PHASE 5: MEMORY UPDATE")
                await self._phase_memory(db, mission, results)

                # Mark as completed
                await self._update_mission_status(db, mission, "completed")
                mission.completed_at = datetime.utcnow()
                await db.commit()

                # Remove from cancelled set if it was there
                self._cancelled_missions.discard(mission_id)

                logger.success(f"✅ Mission #{mission_id} completed successfully!")

            except asyncio.CancelledError:
                logger.warning(f"⚠️ Mission #{mission_id} was cancelled")
                await self._update_mission_status(db, mission, "cancelled")
                self._cancelled_missions.discard(mission_id)
                raise
            except Exception as e:
                logger.error(f"❌ Mission #{mission_id} failed: {e}", exc_info=True)
                error_payload = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "error_trace": traceback.format_exc(limit=8),
                    "error_at": datetime.utcnow().isoformat(),
                }
                mission.mission_metadata = {
                    **(mission.mission_metadata or {}),
                    **error_payload,
                }
                await db.commit()
                await self._update_mission_status(db, mission, "failed")
                self._cancelled_missions.discard(mission_id)
                raise

    async def _phase_plan(self, db: Any, mission: Mission) -> Dict[str, Any]:
        """
        PHASE 1: PLAN
        - Break mission into tasks
        - Consult long-term memory (RAG)
        - Define responsible agents
        """
        logger.info("🔍 Consulting long-term memory...")

        # Query memory for relevant context
        memory_context = await self.memory.search(
            query=f"{mission.title} {mission.description}",
            limit=5,
        )

        # Build context for planning
        context = self._build_planning_context(mission, memory_context)

        # Ask LLM to create plan
        planning_prompt = self._get_planning_prompt(context)
        plan_response = await self.ollama.generate(planning_prompt)

        # Parse plan
        plan = self._parse_plan(plan_response)

        logger.info(f"📋 Created plan with {len(plan['tasks'])} tasks")

        # Create task records
        for task_data in plan["tasks"]:
            task = Task(
                mission_id=mission.id,
                agent_type=task_data["agent"],
                title=task_data["title"],
                description=task_data.get("description"),
                status="pending",
                task_metadata=task_data.get("metadata", {}),
            )
            db.add(task)

        await db.commit()

        return plan

    async def _phase_execute(
        self, db: Any, mission: Mission, plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        PHASE 2: EXECUTE
        - Delegate tasks to specialized agents with parallel execution
        - Monitor execution
        - Respect dependencies between tasks
        """
        logger.info("👥 Delegating tasks to agents...")

        # Get tasks for this mission
        task_result = await db.execute(
            select(Task).where(Task.mission_id == mission.id).order_by(Task.id)
        )
        tasks = list(task_result.scalars().all())

        # Build dependency graph
        task_graph = self._build_task_graph(tasks, plan)

        # Execute tasks in parallel batches based on dependencies
        results = await self._execute_task_graph(db, mission.id, tasks, task_graph)

        return results

    def _build_task_graph(self, tasks: List[Task], plan: Dict[str, Any]) -> Dict[int, List[int]]:
        """
        Build task dependency graph
        Returns: {task_index: [dependent_task_indices]}
        """
        graph = {i: [] for i in range(len(tasks))}

        # Map task titles to indices
        task_title_to_idx = {task.title: i for i, task in enumerate(tasks)}

        # Build dependencies from plan
        plan_tasks = plan.get("tasks", [])
        for i, plan_task in enumerate(plan_tasks):
            if i >= len(tasks):
                break
            dependencies = plan_task.get("dependencies", [])
            for dep_title in dependencies:
                if dep_title in task_title_to_idx:
                    dep_idx = task_title_to_idx[dep_title]
                    graph[i].append(dep_idx)

        return graph

    async def _execute_task_graph(
        self, db: Any, mission_id: int, tasks: List[Task], graph: Dict[int, List[int]]
    ) -> List[Dict[str, Any]]:
        """
        Execute tasks in topological order with parallelism
        """
        completed = set()
        results = [None] * len(tasks)
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

        async def execute_single_task(task: Task, idx: int):
            """Execute a single task with semaphore"""
            async with semaphore:
                try:
                    self._check_cancelled(mission_id)

                    logger.info(f"🤖 Executing task: {task.title} (Agent: {task.agent_type})")

                    # Update task status
                    task.status = "in_progress"
                    task.started_at = datetime.utcnow()
                    await db.commit()

                    # Get agent
                    agent = AgentFactory.create_agent(task.agent_type)

                    # Execute task
                    result = await agent.execute_task(task)

                    # Update task result
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.result = result
                    await db.commit()

                    results[idx] = result
                    completed.add(idx)

                    logger.success(f"✅ Task completed: {task.title}")

                except Exception as e:
                    logger.error(f"❌ Task failed: {task.title} - {e}")
                    task.status = "failed"
                    task.error = str(e)
                    await db.commit()
                    raise

        # Execute tasks in waves based on dependencies
        pending = set(range(len(tasks)))

        while pending:
            # Find tasks ready to execute (all dependencies completed)
            ready = []
            for idx in pending:
                deps = graph.get(idx, [])
                if all(dep in completed for dep in deps):
                    ready.append(idx)

            if not ready:
                # No tasks ready - check for circular dependencies
                if pending:
                    logger.warning(f"⚠️ Circular dependency detected, executing remaining tasks: {pending}")
                    ready = list(pending)
                else:
                    break

            # Execute ready tasks in parallel
            logger.info(f"🚀 Executing batch of {len(ready)} tasks in parallel")
            await asyncio.gather(
                *[execute_single_task(tasks[idx], idx) for idx in ready]
            )

            # Remove completed tasks from pending
            pending -= set(ready)

        return [r for r in results if r is not None]

    async def _phase_validate(self, db: Any, mission: Mission) -> bool:
        """
        PHASE 3: VALIDATE
        - Run lint
        - Run tests
        - Run build
        - Reject if any fails
        """
        validations = []

        # Lint
        logger.info("🔍 Running lint...")
        lint_result = await self.runner_tools.run_lint()
        validations.append(("lint", lint_result))

        # Tests
        logger.info("🧪 Running tests...")
        test_result = await self.runner_tools.run_tests()
        validations.append(("test", test_result))

        # Build
        logger.info("🏗️ Running build...")
        build_result = await self.runner_tools.run_build()
        validations.append(("build", build_result))

        # Check all passed
        all_passed = all(result["success"] for _, result in validations)

        if not all_passed:
            failed = [name for name, result in validations if not result["success"]]
            logger.error(f"❌ Validation failed: {', '.join(failed)}")

        return all_passed

    async def _phase_integrate(self, db: Any, mission: Mission) -> None:
        """
        PHASE 4: INTEGRATE
        - Create branch
        - Commit changes
        - Update docs
        """
        logger.info("🔗 Integrating changes...")

        # Create branch if needed
        branch_name = f"mission-{mission.id}-{mission.title.lower().replace(' ', '-')[:30]}"
        await self.git_tools.create_branch(branch_name)

        # Stage and commit changes
        commit_message = f"{mission.title}\n\n{mission.description}"
        await self.git_tools.commit_changes(commit_message)

        logger.success(f"✅ Changes committed to branch: {branch_name}")

    async def _phase_memory(
        self, db: Any, mission: Mission, results: List[Dict[str, Any]]
    ) -> None:
        """
        PHASE 5: MEMORY
        - Register summary
        - Update ADRs
        - Update embeddings with approved content
        """
        logger.info("🧠 Updating long-term memory...")

        # Create summary
        summary = self._create_mission_summary(mission, results)

        # Save as memory item (pending approval)
        from app.models.memory_item import MemoryItem

        memory_item = MemoryItem(
            type="playbook",
            title=f"Mission: {mission.title}",
            content=summary,
            category="mission_summary",
            approved=False,  # Requires manual approval
            item_metadata={"mission_id": mission.id},
        )
        db.add(memory_item)
        await db.commit()

        logger.success("✅ Memory updated (pending approval)")

    # ━━━ Helper Methods ━━━

    async def _update_mission_status(self, db: Any, mission: Mission, status: str) -> None:
        """Update mission status"""
        mission.status = status
        mission.updated_at = datetime.utcnow()
        await db.commit()

    def _build_planning_context(
        self, mission: Mission, memory_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build context for planning"""
        return {
            "mission": {
                "title": mission.title,
                "description": mission.description,
            },
            "memory": memory_context,
        }

    def _get_planning_prompt(self, context: Dict[str, Any]) -> str:
        """Generate planning prompt"""
        memory_text = "\n\n".join(
            [f"- {item['title']}: {item['content'][:200]}..." for item in context["memory"]]
        )

        return f"""You are an expert development orchestrator. Create a detailed plan to accomplish this mission.

MISSION:
Title: {context['mission']['title']}
Description: {context['mission']['description']}

RELEVANT KNOWLEDGE FROM MEMORY:
{memory_text if memory_text else "No relevant prior knowledge found."}

Create a plan with specific tasks. For each task, specify:
1. Title
2. Description
3. Responsible agent (frontend, backend, database, qa, devops, security, documentation)
4. Dependencies (if any)

Return a JSON array of tasks in this format:
[
  {{
    "title": "Task title",
    "description": "What needs to be done",
    "agent": "backend",
    "dependencies": []
  }}
]
"""

    def _parse_plan(self, plan_response: str) -> Dict[str, Any]:
        """Parse plan from LLM response"""
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON array
            match = re.search(r'\[[\s\S]*\]', plan_response)
            if match:
                tasks = json.loads(match.group(0))
            else:
                # Fallback: create basic task
                tasks = [
                    {
                        "title": "Implement mission requirements",
                        "description": "Complete the mission as described",
                        "agent": "backend",
                        "dependencies": [],
                    }
                ]

            return {"tasks": tasks, "raw_response": plan_response}

        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            # Return minimal plan
            return {
                "tasks": [
                    {
                        "title": "Implement mission requirements",
                        "description": "Complete the mission as described",
                        "agent": "backend",
                        "dependencies": [],
                    }
                ],
                "raw_response": plan_response,
            }

    def _create_mission_summary(
        self, mission: Mission, results: List[Dict[str, Any]]
    ) -> str:
        """Create mission summary for memory"""
        summary = f"""# Mission: {mission.title}

## Description
{mission.description}

## Execution Summary
- Status: {mission.status}
- Started: {mission.created_at}
- Completed: {mission.completed_at}

## Tasks Completed
{len(results)} tasks were executed successfully.

## Key Learnings
(To be filled in with specific insights from this mission)

## Related ADRs
(To be linked)
"""
        return summary
