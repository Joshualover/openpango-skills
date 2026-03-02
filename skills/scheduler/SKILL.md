---
name: scheduler
description: Task scheduling and cron-like job management
version: 1.0.0
dependencies:
  - memory
---

# Scheduler Skill

Cron-like task scheduling for automated agent workflows.

## Features

- Cron expression parsing
- Scheduled task execution
- Task queue management
- Persistence across restarts

## Usage

```python
from scheduler import TaskScheduler

scheduler = TaskScheduler()

# Schedule recurring task
scheduler.schedule("0 * * * *", "hourly_report")

# Schedule one-time task
scheduler.schedule_once("2026-03-02T15:00:00Z", "send_reminder")
```
