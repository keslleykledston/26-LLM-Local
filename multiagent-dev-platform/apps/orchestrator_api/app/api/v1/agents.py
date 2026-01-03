"""
Agents API endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_agents():
    """List all available agents and their capabilities"""
    return {
        "agents": [
            {
                "type": "orchestrator",
                "name": "Orchestrator / Planner",
                "description": "Coordinates all agents, plans missions, manages pipeline",
                "tools": ["memory", "external_ai", "delegation", "validation"],
                "required": True,
            },
            {
                "type": "frontend",
                "name": "Frontend Developer",
                "description": "React, Next.js, TypeScript, CSS, UI/UX implementation",
                "tools": ["repo", "git", "npm", "memory"],
                "required": True,
            },
            {
                "type": "backend",
                "name": "Backend Developer",
                "description": "Python, FastAPI, APIs, business logic, integrations",
                "tools": ["repo", "git", "python", "memory"],
                "required": True,
            },
            {
                "type": "database",
                "name": "Database / Performance Specialist",
                "description": "SQL, indexes, query optimization, data modeling",
                "tools": ["repo", "git", "database", "memory"],
                "required": True,
            },
            {
                "type": "qa",
                "name": "QA + UX Specialist",
                "description": "Testing, validation, user experience, accessibility",
                "tools": ["repo", "test", "lint", "memory"],
                "required": True,
            },
            {
                "type": "devops",
                "name": "DevOps / SRE",
                "description": "Docker, CI/CD, deployment, monitoring, infrastructure",
                "tools": ["repo", "git", "docker", "shell", "memory"],
                "required": False,
            },
            {
                "type": "security",
                "name": "Security Reviewer",
                "description": "Security audits, vulnerability scanning, best practices",
                "tools": ["repo", "security_scan", "memory"],
                "required": False,
            },
            {
                "type": "documentation",
                "name": "Documentation Agent",
                "description": "README, API docs, guides, comments, ADRs",
                "tools": ["repo", "git", "memory"],
                "required": False,
            },
        ]
    }


@router.get("/{agent_type}")
async def get_agent_info(agent_type: str):
    """Get detailed information about a specific agent"""
    agents = await list_agents()
    agent = next((a for a in agents["agents"] if a["type"] == agent_type), None)

    if not agent:
        return {"error": "Agent not found"}, 404

    return agent
