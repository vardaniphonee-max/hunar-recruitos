from typing import Any
import httpx

from ..schemas import CandidateResult, SearchCriteria
from .base import PeopleSearchProvider


class ApolloPeopleSearchProvider(PeopleSearchProvider):
    """Apollo People API Search adapter.

    Search results intentionally do not claim to include phone or email data;
    Apollo documents those as separate enrichment operations.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def search(self, criteria: SearchCriteria) -> tuple[list[CandidateResult], dict[str, Any]]:
        params: list[tuple[str, str | int | bool]] = [
            ("page", criteria.page),
            ("per_page", criteria.per_page),
            ("include_similar_titles", True),
        ]
        params.extend(("person_titles[]", value) for value in criteria.titles)
        params.extend(("person_locations[]", value) for value in criteria.locations)
        if criteria.keywords:
            params.append(("q_keywords", " ".join(criteria.keywords)))

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/mixed_people/api_search",
                params=params,
                headers={"x-api-key": self.api_key, "accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()

        normalized = []
        for person in payload.get("people", []):
            organization = person.get("organization") or {}
            normalized.append(
                CandidateResult(
                    external_id=str(person.get("id")),
                    source="apollo",
                    is_demo=False,
                    name=person.get("name") or "Name unavailable",
                    title=person.get("title") or "Title unavailable",
                    company=organization.get("name") or "Company unavailable",
                    location=person.get("city") or person.get("state") or person.get("country") or "Location unavailable",
                    experience_years=0,
                    skills=[],
                    match_score=70,
                    match_reasons=["Matches requested title or keyword filters"],
                )
            )
        return normalized, payload
