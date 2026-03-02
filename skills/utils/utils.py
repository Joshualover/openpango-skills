"""
Utility functions for OpenPango
Common helpers for file ops, data processing, etc.
"""

import json
import csv
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


class FileUtils:
    """File operation utilities."""
    
    @staticmethod
    def read_file(path: str) -> str:
        """Read file contents."""
        return Path(path).read_text()
    
    @staticmethod
    def write_file(path: str, content: str):
        """Write content to file."""
        Path(path).write_text(content)
    
    @staticmethod
    def copy_dir(src: str, dst: str):
        """Copy directory recursively."""
        shutil.copytree(src, dst, dirs_exist_ok=True)
    
    @staticmethod
    def list_files(dir_path: str, pattern: str = "*") -> List[str]:
        """List files matching pattern."""
        return [str(p) for p in Path(dir_path).glob(pattern)]


class DataUtils:
    """Data processing utilities."""
    
    @staticmethod
    def to_json(data: Any, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(data, indent=indent)
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        """Parse JSON string."""
        return json.loads(json_str)
    
    @staticmethod
    def to_csv(data: List[Dict], path: str):
        """Write data to CSV file."""
        if not data:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def now_iso() -> str:
        """Get current UTC time in ISO format."""
        return datetime.utcnow().isoformat() + "Z"


if __name__ == "__main__":
    print("Utils module ready")
