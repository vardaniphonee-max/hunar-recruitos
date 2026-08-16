from typing import Any
import httpx

from .base import VoiceProvider


class HunarVoiceProvider(VoiceProvider):
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def create_call(
        self,
        *,
        agent_id: str,
        callee_name: str,
        mobile_number: str,
        custom_data: dict[str, Any],
        request_id: str,
        callback_config: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "agent_id": agent_id,
            "callee_name": callee_name,
            "mobile_number": mobile_number,
            "custom_data": custom_data,
            "request_id": request_id,
            "retry_config": {"max_retry_count": 1, "retry_interval_hours": 3},
            "timezone": "Asia/Kolkata",
        }
        if callback_config:
            body["callback_config"] = callback_config
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/calls/", headers=self.headers, json=body)
            response.raise_for_status()
            return response.json()

    async def get_call(self, provider_call_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/calls/{provider_call_id}/", headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def list_agents(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}/agents/", headers=self.headers)
            response.raise_for_status()
            return response.json()
