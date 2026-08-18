"""
DriftLens - Auto Git Puller
Pulls latest drift-results.json from GitHub
every 60 seconds automatically.
"""

import subprocess
import threading
import time
import logging
import os

logger = logging.getLogger(__name__)


class GitPuller:
    """Automatically pulls latest results from GitHub."""

    def __init__(self, interval: int = 60):
        self.interval = interval
        self._thread = None
        self._running = False

    def _pull(self):
        """Run git pull to get latest results."""
        try:
            # Find repo root
            result = subprocess.run(
                ["git", "pull", "--no-rebase"],
                capture_output=True,
                text=True,
                cwd=self._find_repo_root(),
                timeout=30,
            )
            if result.returncode == 0:
                if "drift-results.json" in result.stdout:
                    logger.info(
                        "✅ New drift results pulled!"
                    )
                else:
                    logger.debug("Git pull: up to date")
            else:
                logger.warning(
                    f"Git pull failed: {result.stderr}"
                )
        except Exception as e:
            logger.debug(f"Git pull skipped: {e}")

    def _find_repo_root(self) -> str:
        """Find git repo root directory."""
        paths = [
            "/app",
            "/repo",
            os.path.expanduser("~"),
            os.getcwd(),
        ]
        for path in paths:
            if os.path.exists(
                os.path.join(path, ".git")
            ):
                return path
        return os.getcwd()

    def _run(self):
        """Background thread runner."""
        logger.info(
            f"🔄 Git puller started "
            f"(interval: {self.interval}s)"
        )
        while self._running:
            self._pull()
            time.sleep(self.interval)

    def start(self):
        """Start background git puller."""
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="git-puller",
        )
        self._thread.start()

    def stop(self):
        """Stop background git puller."""
        self._running = False


# Global instance
git_puller = GitPuller(interval=60)
