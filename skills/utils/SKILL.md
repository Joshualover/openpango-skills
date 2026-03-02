---
name: utils
description: Common utility functions for file operations, data processing, and helpers
version: 1.0.0
dependencies: []
---

# Utilities Skill

Common helper functions for everyday tasks.

## Features

- File operations (read, write, convert)
- Data formatting (JSON, CSV, YAML)
- String manipulation
- Date/time utilities

## Usage

```python
from utils import FileUtils, DataUtils

files = FileUtils()
files.copy_dir("src", "dist")

data = DataUtils()
json_data = data.to_json({"key": "value"})
```
