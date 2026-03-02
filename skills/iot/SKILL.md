---
name: iot
description: IoT and Home Assistant integration for smart home control
version: 1.0.0
dependencies: []
---

# IoT Skill

Home Assistant and smart home device integration.

## Features

- Home Assistant REST/WebSocket API
- Device state queries
- Service calls (lights, switches, climate)
- Secure token storage

## Usage

```python
from home_assistant import HomeAssistantClient

ha = HomeAssistantClient("http://localhost:8123", "token")

# Get device state
state = ha.get_device_state("light.living_room")

# Call service
ha.call_service("light", "turn_on", {"entity_id": "light.living_room"})
```
