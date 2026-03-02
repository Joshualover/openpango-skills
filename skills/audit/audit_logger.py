"""
Immutable Audit Logger for OpenPango
Cryptographically-secured audit logging with hash chaining
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """Immutable audit logger with cryptographic hash chaining."""
    
    def __init__(self, log_path: str = None):
        self.log_path = Path(log_path or os.path.expanduser(
            "~/.openclaw/workspace/audit_log.jsonl"
        ))
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._get_last_hash()
    
    def _get_last_hash(self) -> str:
        """Get the hash of the last log entry."""
        if not self.log_path.exists():
            return "0" * 64  # Genesis hash
        
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                return "0" * 64
            last_entry = json.loads(lines[-1])
            return last_entry.get("entry_hash", "0" * 64)
    
    def _compute_entry_hash(self, entry: dict, prev_hash: str) -> str:
        """Compute hash for an entry including previous hash."""
        entry_data = {
            "prev_hash": prev_hash,
            "timestamp": entry["timestamp"],
            "action_type": entry["action_type"],
            "payload": entry["payload"]
        }
        return hashlib.sha256(
            json.dumps(entry_data, sort_keys=True).encode()
        ).hexdigest()
    
    def log_action(self, action_type: str, payload: dict, metadata: dict = None) -> str:
        """
        Log an action to the audit trail.
        
        Args:
            action_type: Type of action (tool_call, file_modify, http_request, etc.)
            payload: Action details
            metadata: Optional metadata (agent_id, session_id, etc.)
        
        Returns:
            Entry hash
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action_type": action_type,
            "payload": payload,
            "metadata": metadata or {},
            "prev_hash": self._last_hash,
        }
        
        entry["entry_hash"] = self._compute_entry_hash(entry, self._last_hash)
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        self._last_hash = entry["entry_hash"]
        return entry["entry_hash"]
    
    def verify_integrity(self) -> tuple[bool, list]:
        """
        Verify the integrity of the audit log.
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        if not self.log_path.exists():
            return True, []
        
        errors = []
        prev_hash = "0" * 64
        
        with open(self.log_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
                    continue
                
                # Verify previous hash linkage
                if entry.get("prev_hash") != prev_hash:
                    errors.append(
                        f"Line {line_num}: Hash chain broken. "
                        f"Expected {prev_hash[:16]}..., got {entry.get('prev_hash', '')[:16]}..."
                    )
                
                # Verify entry hash
                expected_hash = self._compute_entry_hash(entry, entry.get("prev_hash", ""))
                if entry.get("entry_hash") != expected_hash:
                    errors.append(
                        f"Line {line_num}: Entry hash mismatch. "
                        f"Entry may have been tampered with."
                    )
                
                prev_hash = entry.get("entry_hash", "")
        
        return len(errors) == 0, errors
    
    def get_stats(self) -> dict:
        """Get audit log statistics."""
        if not self.log_path.exists():
            return {"total_entries": 0, "action_types": {}}
        
        action_counts = {}
        total = 0
        
        with open(self.log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    action_type = entry.get("action_type", "unknown")
                    action_counts[action_type] = action_counts.get(action_type, 0) + 1
                    total += 1
                except:
                    pass
        
        return {
            "total_entries": total,
            "action_types": action_counts,
            "log_path": str(self.log_path)
        }


# CLI integration
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit Log Manager")
    parser.add_argument("--verify", action="store_true", help="Verify log integrity")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--log", type=str, help="Log a test action")
    
    args = parser.parse_args()
    
    logger = AuditLogger()
    
    if args.verify:
        is_valid, errors = logger.verify_integrity()
        if is_valid:
            print("✅ Audit log integrity verified")
        else:
            print("❌ Audit log integrity check FAILED:")
            for error in errors:
                print(f"  - {error}")
            exit(1)
    
    if args.stats:
        stats = logger.get_stats()
        print(f"Total entries: {stats['total_entries']}")
        print(f"Action types: {json.dumps(stats['action_types'], indent=2)}")
    
    if args.log:
        entry_hash = logger.log_action("cli_test", {"message": args.log})
        print(f"Logged action with hash: {entry_hash[:16]}...")


if __name__ == "__main__":
    main()
