"""
Git Tools - Git operations
"""
from git import Repo, GitCommandError
from typing import List, Dict, Any, Optional
from loguru import logger
import os


class GitTools:
    """Tools for Git operations"""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or os.getcwd()
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            logger.warning(f"Not a git repository: {e}")
            self.repo = None

    async def get_status(self) -> Dict[str, Any]:
        """Get git status"""
        if not self.repo:
            return {"error": "Not a git repository"}

        try:
            return {
                "branch": self.repo.active_branch.name,
                "modified": [item.a_path for item in self.repo.index.diff(None)],
                "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
                "untracked": self.repo.untracked_files,
                "is_dirty": self.repo.is_dirty(),
            }
        except Exception as e:
            logger.error(f"Git status failed: {e}")
            return {"error": str(e)}

    async def get_diff(self, staged: bool = False) -> str:
        """Get git diff"""
        if not self.repo:
            return ""

        try:
            if staged:
                return self.repo.git.diff("--staged")
            else:
                return self.repo.git.diff()
        except Exception as e:
            logger.error(f"Git diff failed: {e}")
            return ""

    async def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        if not self.repo:
            return False

        try:
            # Check if branch exists
            if branch_name in self.repo.heads:
                logger.info(f"Branch {branch_name} already exists, checking out")
                self.repo.git.checkout(branch_name)
            else:
                # Create new branch
                self.repo.git.checkout("-b", branch_name)
                logger.success(f"✅ Created and checked out branch: {branch_name}")

            return True
        except Exception as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False

    async def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """Commit changes"""
        if not self.repo:
            return False

        try:
            # Stage files
            if files:
                self.repo.index.add(files)
            else:
                # Stage all
                self.repo.git.add("--all")

            # Commit
            self.repo.index.commit(message)
            logger.success(f"✅ Committed: {message}")
            return True

        except Exception as e:
            logger.error(f"Git commit failed: {e}")
            return False

    async def push(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """Push to remote"""
        if not self.repo:
            return False

        try:
            branch = branch or self.repo.active_branch.name
            self.repo.git.push(remote, branch)
            logger.success(f"✅ Pushed to {remote}/{branch}")
            return True

        except Exception as e:
            logger.error(f"Git push failed: {e}")
            return False

    async def get_log(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """Get commit log"""
        if not self.repo:
            return []

        try:
            commits = []
            for commit in list(self.repo.iter_commits(max_count=max_count)):
                commits.append(
                    {
                        "sha": commit.hexsha[:8],
                        "author": str(commit.author),
                        "date": commit.committed_datetime.isoformat(),
                        "message": commit.message.strip(),
                    }
                )
            return commits

        except Exception as e:
            logger.error(f"Git log failed: {e}")
            return []
