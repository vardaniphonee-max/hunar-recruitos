from abc import ABC, abstractmethod
from typing import Any

from ..schemas import CandidateResult, SearchCriteria


class PeopleSearchProvider(ABC):
    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> tuple[list[CandidateResult], dict[str, Any]]:
        raise NotImplementedError


class VoiceProvider(ABC):
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def get_call(self, provider_call_id: str) -> dict[str, Any]:
        raise NotImplementedError
