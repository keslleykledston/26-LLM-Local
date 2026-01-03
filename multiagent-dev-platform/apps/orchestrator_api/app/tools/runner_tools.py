"""
Runner Tools - Execute tests, lint, build
"""
import asyncio
import os
from typing import Dict, Any, Optional
from loguru import logger


class RunnerTools:
    """Tools for running tests, linters, builds"""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or os.getcwd()

    async def _run_command(
        self, command: str, cwd: Optional[str] = None, timeout: int = 300
    ) -> Dict[str, Any]:
        """Run a shell command"""
        try:
            cwd = cwd or self.repo_path

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Command timed out",
                    "exit_code": -1,
                }

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore"),
                "exit_code": process.returncode,
            }

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}

    async def run_lint(self, path: str = ".") -> Dict[str, Any]:
        """Run linting"""
        logger.info("🔍 Running lint...")

        # Try common linters
        commands = [
            "npm run lint 2>&1",
            "flake8 .",
            "black --check .",
            "eslint .",
        ]

        for command in commands:
            result = await self._run_command(command)
            if result["exit_code"] != 127:  # Not "command not found"
                return {
                    "success": result["success"],
                    "output": result["stdout"] + result["stderr"],
                    "linter": command.split()[0],
                }

        # No linter found
        logger.warning("⚠️ No linter configured")
        return {
            "success": True,
            "output": "No linter configured (skipped)",
            "linter": "none",
        }

    async def run_tests(self, path: str = ".") -> Dict[str, Any]:
        """Run tests"""
        logger.info("🧪 Running tests...")

        # Try common test runners
        commands = [
            "npm test -- --passWithNoTests 2>&1",
            "pytest -v",
            "python -m pytest",
            "npm run test:ci 2>&1",
        ]

        for command in commands:
            result = await self._run_command(command, timeout=600)
            if result["exit_code"] != 127:  # Not "command not found"
                return {
                    "success": result["success"],
                    "output": result["stdout"] + result["stderr"],
                    "runner": command.split()[0],
                }

        # No test runner found
        logger.warning("⚠️ No test runner configured")
        return {
            "success": True,
            "output": "No test runner configured (skipped)",
            "runner": "none",
        }

    async def run_build(self, path: str = ".") -> Dict[str, Any]:
        """Run build"""
        logger.info("🏗️ Running build...")

        # Try common build commands
        commands = [
            "npm run build 2>&1",
            "python setup.py build",
            "make build",
        ]

        for command in commands:
            result = await self._run_command(command, timeout=900)
            if result["exit_code"] != 127:  # Not "command not found"
                return {
                    "success": result["success"],
                    "output": result["stdout"] + result["stderr"],
                    "builder": command.split()[0],
                }

        # No builder found
        logger.warning("⚠️ No build command configured")
        return {
            "success": True,
            "output": "No build command configured (skipped)",
            "builder": "none",
        }

    async def run_custom_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a custom command"""
        logger.info(f"⚙️ Running: {command}")
        return await self._run_command(command, timeout=timeout)
