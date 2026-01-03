"""
Repository Tools - File operations, search, patches
"""
import os
import glob
import re
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from loguru import logger


class RepoTools:
    """Tools for repository file operations"""

    # Directories to ignore during file operations
    IGNORE_DIRS = {
        "node_modules", ".next", ".venv", "venv", "env", "__pycache__",
        ".git", ".pytest_cache", "dist", "build", ".tox", ".eggs",
        "qdrant_storage", "qdrant_data", "postgres_data", ".turbo"
    }

    # File patterns to ignore
    IGNORE_PATTERNS = {
        "*.pyc", "*.pyo", "*.so", "*.dylib", "*.dll",
        ".DS_Store", "Thumbs.db", "*.log", "*.tmp"
    }

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or os.getcwd()
        self.gitignore_patterns = self._load_gitignore()
        self.has_ripgrep = shutil.which("rg") is not None

    async def read_file(self, file_path: str) -> str:
        """Read file contents"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    async def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.success(f"✅ Wrote file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False

    def _load_gitignore(self) -> Set[str]:
        """Load patterns from .gitignore"""
        patterns = set()
        gitignore_path = os.path.join(self.repo_path, ".gitignore")

        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.add(line)
            except Exception as e:
                logger.warning(f"Failed to load .gitignore: {e}")

        return patterns

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored"""
        path_parts = Path(path).parts

        # Check if any directory in path is in ignore list
        for part in path_parts:
            if part in self.IGNORE_DIRS:
                return True

        # Check file patterns
        for pattern in self.IGNORE_PATTERNS:
            if Path(path).match(pattern):
                return True

        return False

    async def search_text(
        self, pattern: str, file_pattern: str = "**/*", case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for text pattern in files (uses ripgrep if available)"""
        try:
            # Use ripgrep if available (much faster)
            if self.has_ripgrep:
                return await self._search_with_ripgrep(pattern, file_pattern, case_sensitive)

            # Fallback to Python implementation
            results = []
            flags = 0 if case_sensitive else re.IGNORECASE

            # Find matching files
            search_pattern = os.path.join(self.repo_path, file_pattern)
            for file_path in glob.glob(search_pattern, recursive=True):
                # Skip ignored paths
                rel_path = os.path.relpath(file_path, self.repo_path)
                if self._should_ignore(rel_path):
                    continue

                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            for line_num, line in enumerate(f, 1):
                                if re.search(pattern, line, flags):
                                    results.append(
                                        {
                                            "file": rel_path,
                                            "line": line_num,
                                            "content": line.strip(),
                                        }
                                    )
                    except (UnicodeDecodeError, PermissionError):
                        continue

            logger.info(f"🔍 Found {len(results)} matches for pattern: {pattern}")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def _search_with_ripgrep(
        self, pattern: str, file_pattern: str = "**/*", case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """Search using ripgrep for better performance"""
        try:
            cmd = ["rg", "--json", pattern]

            if not case_sensitive:
                cmd.append("-i")

            # Add glob pattern if specified
            if file_pattern != "**/*":
                cmd.extend(["-g", file_pattern])

            # Run ripgrep
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse JSON output
            import json
            results = []
            for line in result.stdout.splitlines():
                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data.get("data", {})
                        results.append({
                            "file": match_data.get("path", {}).get("text", ""),
                            "line": match_data.get("line_number", 0),
                            "content": match_data.get("lines", {}).get("text", "").strip()
                        })
                except json.JSONDecodeError:
                    continue

            logger.info(f"🔍 Found {len(results)} matches with ripgrep for: {pattern}")
            return results

        except subprocess.TimeoutExpired:
            logger.warning("Ripgrep search timed out, falling back to Python search")
            return []
        except Exception as e:
            logger.warning(f"Ripgrep search failed ({e}), falling back to Python search")
            return []

    async def apply_patch(self, file_path: str, old_text: str, new_text: str) -> bool:
        """Apply a patch to a file"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if old_text not in content:
                logger.error(f"Old text not found in {file_path}")
                return False

            new_content = content.replace(old_text, new_text, 1)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.success(f"✅ Patched file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to patch file {file_path}: {e}")
            return False

    async def list_files(
        self, directory: str = ".", pattern: str = "*", recursive: bool = False
    ) -> List[str]:
        """List files in directory (respects .gitignore and ignore rules)"""
        try:
            search_path = os.path.join(self.repo_path, directory)
            if recursive:
                glob_pattern = os.path.join(search_path, "**", pattern)
                files = glob.glob(glob_pattern, recursive=True)
            else:
                glob_pattern = os.path.join(search_path, pattern)
                files = glob.glob(glob_pattern)

            # Filter only files and apply ignore rules
            filtered_files = []
            for f in files:
                if os.path.isfile(f):
                    rel_path = os.path.relpath(f, self.repo_path)
                    if not self._should_ignore(rel_path):
                        filtered_files.append(rel_path)

            return sorted(filtered_files)

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = os.path.join(self.repo_path, file_path)
        return os.path.isfile(full_path)

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            os.remove(full_path)
            logger.success(f"✅ Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
