---
name: hitl
description: Human-in-the-Loop approval workflow for sensitive actions
version: 1.0.0
dependencies:
  - memory
---

# HITL Approval Skill

Human-in-the-Loop approval system for sensitive agent actions.

## Features

- Approval request management
- CLI prompts for terminal approval
- Web UI integration hooks
- Action pause/resume

## Usage

```python
from approval_manager import ApprovalManager

approver = ApprovalManager()

# Request approval
approved = approver.request_approval(
    action="send_email",
    details={"to": "user@example.com", "subject": "Test"},
    reason="Sending email requires approval"
)

if approved:
    # Proceed with action
    pass
```
