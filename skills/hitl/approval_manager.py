"""
HITL Approval Manager for OpenPango
Human-in-the-Loop workflow for sensitive actions
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class ApprovalManager:
    """Manage human approval requests for sensitive actions."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir or os.path.expanduser(
            "~/.openclaw/workspace/approvals"
        ))
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.pending_file = self.workspace_dir / "pending.json"
        self._load_pending()
    
    def _load_pending(self):
        """Load pending approvals from file."""
        if self.pending_file.exists():
            with open(self.pending_file) as f:
                self.pending = json.load(f)
        else:
            self.pending = []
    
    def _save_pending(self):
        """Save pending approvals to file."""
        with open(self.pending_file, 'w') as f:
            json.dump(self.pending, f, indent=2)
    
    def request_approval(self, action: str, details: Dict, 
                        reason: str = None) -> bool:
        """
        Request human approval for an action.
        
        Returns True if approved, False if rejected.
        Blocks until decision is made.
        """
        request_id = f"{datetime.utcnow().timestamp()}"
        
        approval_request = {
            "id": request_id,
            "action": action,
            "details": details,
            "reason": reason or "Sensitive action requires approval",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "pending"
        }
        
        self.pending.append(approval_request)
        self._save_pending()
        
        # CLI prompt
        print(f"\n{'='*60}")
        print(f"⚠️  APPROVAL REQUIRED")
        print(f"{'='*60}")
        print(f"Action: {action}")
        print(f"Reason: {reason}")
        print(f"Details: {json.dumps(details, indent=2)}")
        print(f"{'='*60}")
        
        while True:
            response = input("Approve? (y/n): ").strip().lower()
            if response in ('y', 'yes'):
                approval_request["status"] = "approved"
                approval_request["decided_at"] = datetime.utcnow().isoformat() + "Z"
                self._save_pending()
                return True
            elif response in ('n', 'no'):
                approval_request["status"] = "rejected"
                approval_request["decided_at"] = datetime.utcnow().isoformat() + "Z"
                self._save_pending()
                return False
            print("Please enter 'y' or 'n'")
    
    def list_pending(self) -> list:
        """List all pending approval requests."""
        self._load_pending()
        return [r for r in self.pending if r["status"] == "pending"]
    
    def approve(self, request_id: str) -> bool:
        """Approve a request by ID."""
        self._load_pending()
        for req in self.pending:
            if req["id"] == request_id:
                req["status"] = "approved"
                req["decided_at"] = datetime.utcnow().isoformat() + "Z"
                self._save_pending()
                return True
        return False
    
    def reject(self, request_id: str) -> bool:
        """Reject a request by ID."""
        self._load_pending()
        for req in self.pending:
            if req["id"] == request_id:
                req["status"] = "rejected"
                req["decided_at"] = datetime.utcnow().isoformat() + "Z"
                self._save_pending()
                return True
        return False


if __name__ == "__main__":
    import sys
    mgr = ApprovalManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            pending = mgr.list_pending()
            print(f"Pending approvals: {len(pending)}")
            for p in pending:
                print(f"  - {p['id']}: {p['action']}")
    else:
        print("HITL Approval Manager ready")
