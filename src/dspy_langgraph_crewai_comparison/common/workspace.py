"""Simple workspace for dumping intermediate steps."""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


class Workspace:
    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.workspace_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Workspace: {self.run_dir}")

    def dump(self, name: str, data: Any, as_pickle: bool = False) -> Path:
        """Dump data to workspace."""
        if as_pickle:
            filepath = self.run_dir / f"{name}.pkl"
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
        else:
            filepath = self.run_dir / f"{name}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"  💾 Saved: {filepath.name}")
        return filepath

    def load(self, name: str, as_pickle: bool = False) -> Any:
        """Load data from workspace."""
        if as_pickle:
            filepath = self.run_dir / f"{name}.pkl"
            with open(filepath, "rb") as f:
                return pickle.load(f)
        else:
            filepath = self.run_dir / f"{name}.json"
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
