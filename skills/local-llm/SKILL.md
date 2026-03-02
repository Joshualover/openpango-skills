---
name: local-llm
description: Local LLM integration with Ollama/vLLM support for offline inference
version: 1.0.0
dependencies: []
---

# Local LLM Skill

Privacy-focused local LLM integration supporting Ollama, vLLM, and other local inference servers.

## Features

- Ollama integration (Llama 3, Mistral, etc.)
- vLLM support for high-throughput inference
- ChatML and Llama-3 prompt formatting
- Seamless backend switching via CLI config
- Offline-capable inference

## Usage

```python
from llm_manager import LocalLLMManager

llm = LocalLLMManager(backend="ollama", model="llama3")

# Generate completion
response = llm.generate("Explain quantum computing")

# Chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
]
response = llm.chat(messages)
```

```bash
openpango config set llm local
openpango config set llm.model llama3
openpango config set llm.backend ollama
```
