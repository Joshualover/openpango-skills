"""
Task Scheduler for OpenPango
Cron-like scheduling for automated workflows
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List
import os


class TaskScheduler:
    """Simple task scheduler with cron support."""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or os.path.expanduser(
            "~/.openclaw/workspace/scheduler.json"
        ))
        self.tasks: List[Dict] = []
        self._load()
    
    def _load(self):
        """Load scheduled tasks from storage."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                self.tasks = json.load(f)
    
    def _save(self):
        """Save tasks to storage."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def schedule(self, cron_expr: str, task_name: str, 
                callback: Callable = None) -> str:
        """Schedule a recurring task."""
        task_id = f"task_{len(self.tasks)}_{datetime.utcnow().timestamp()}"
        task = {
            "id": task_id,
            "type": "cron",
            "cron": cron_expr,
            "name": task_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "enabled": True
        }
        self.tasks.append(task)
        self._save()
        return task_id
    
    def schedule_once(self, run_at: str, task_name: str) -> str:
        """Schedule a one-time task."""
        task_id = f"once_{datetime.utcnow().timestamp()}"
        task = {
            "id": task_id,
            "type": "once",
            "run_at": run_at,
            "name": task_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "enabled": True
        }
        self.tasks.append(task)
        self._save()
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["enabled"] = False
                self._save()
                return True
        return False
    
    def list_tasks(self) -> List[Dict]:
        """List all scheduled tasks."""
        return self.tasks
    
    def get_due_tasks(self) -> List[Dict]:
        """Get tasks that are due to run."""
        now = datetime.utcnow()
        due = []
        for task in self.tasks:
            if not task.get("enabled", True):
                continue
            if task["type"] == "once":
                run_at = datetime.fromisoformat(task["run_at"].replace("Z", ""))
                if run_at <= now:
                    due.append(task)
        return due


if __name__ == "__main__":
    scheduler = TaskScheduler()
    print(f"Scheduled tasks: {len(scheduler.list_tasks())}")
