---
name: audit
description: Immutable audit logging for enterprise compliance with cryptographic hash chaining
version: 1.0.0
dependencies:
  - memory
---

# Audit Logging Skill

Provides immutable, cryptographically-secured audit logging for all agent actions.

## Features

- Cryptographic hash chaining (each entry hashes the previous)
- Tamper detection via `--verify` command
- Logs all tool invocations, HTTP requests, file modifications
- CLI command: `openpango audit [--verify]`

## Usage

```python
from audit_logger import AuditLogger

logger = AuditLogger()
logger.log_action("tool_call", {"tool": "web_search", "query": "test"})
logger.log_action("file_modify", {"path": "/tmp/test.txt", "action": "write"})
```

```bash
openpango audit --verify  # Verify log integrity
```
