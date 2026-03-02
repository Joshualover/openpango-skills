"""
Home Assistant Client for OpenPango
IoT and smart home integration
"""

import requests
from typing import Optional, Dict


class HomeAssistantClient:
    """Home Assistant API client."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_device_state(self, entity_id: str) -> Dict:
        """Get state of a device entity."""
        url = f"{self.base_url}/api/states/{entity_id}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return {"success": True, "state": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def call_service(self, domain: str, service: str, data: Dict = None) -> Dict:
        """Call a Home Assistant service."""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        try:
            resp = requests.post(url, headers=self.headers, json=data or {}, timeout=10)
            resp.raise_for_status()
            return {"success": True, "result": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import os
    ha = HomeAssistantClient(
        os.getenv("HA_URL", "http://localhost:8123"),
        os.getenv("HA_TOKEN", "")
    )
    print("Home Assistant client ready")
