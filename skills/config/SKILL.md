---
name: config
description: Configuration management with validation and environment support
version: 1.0.0
dependencies: []
---

# Config Skill

Centralized configuration management.

## Features

- YAML/JSON config loading
- Environment variable overrides
- Schema validation
- Hot reloading

## Usage

```python
from config_manager import ConfigManager

config = ConfigManager("config.yaml")
db_url = config.get("database.url")
```
