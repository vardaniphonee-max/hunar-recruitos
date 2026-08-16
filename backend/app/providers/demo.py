from typing import Any
from uuid import uuid4

from ..schemas import CandidateResult, SearchCriteria
from .base import PeopleSearchProvider, VoiceProvider


class DemoPeopleSearchProvider(PeopleSearchProvider):
    async def search(self, criteria: SearchCriteria) -> tuple[list[CandidateResult], dict[str, Any]]:
        rows = [
            ("demo-ananya", "Ananya Rao", "Senior Customer Success Manager", "Chargebee", "Bengaluru, India", 7, ["B2B SaaS", "Enterprise accounts", "Onboarding"], 94),
            ("demo-rohan", "Rohan Mehta", "Customer Success Lead", "Freshworks", "Chennai, India", 6, ["SaaS", "Team leadership", "Retention"], 89),
            ("demo-nisha", "Nisha Verma", "Enterprise Success Partner", "Darwinbox", "Hyderabad, India", 8, ["Enterprise SaaS", "Renewals", "QBRs"], 86),
            ("demo-kabir", "Kabir Shah", "Customer Experience Manager", "Razorpay", "Mumbai, India", 5, ["Fintech", "Escalations", "Analytics"], 81),
        ]
        results = [
            CandidateResult(
                external_id=row[0], source="demo-apollo", is_demo=True, name=row[1], title=row[2],
                company=row[3], location=row[4], experience_years=row[5], skills=row[6],
                phone=None, email=None, match_score=row[7],
                match_reasons=["Title alignment", "Relevant skills", "Experience range"],
            )
            for row in rows
        ]
        return results, {"demo": True, "total_entries": len(results)}


class DemoVoiceProvider(VoiceProvider):
    async def create_call(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "id": f"demo-call-{uuid4()}",
            "request_id": kwargs["request_id"],
            "status": "NOT_STARTED",
            "lifecycle_status": "NOT_STARTED",
            "callee_name": kwargs["callee_name"],
            "mobile_number": kwargs["mobile_number"],
            "is_demo": True,
        }

    async def get_call(self, provider_call_id: str) -> dict[str, Any]:
        return {
            "id": provider_call_id,
            "status": "COMPLETED",
            "lifecycle_status": "COMPLETED",
            "duration_seconds": 278,
            "recording_url": None,
            "result": {
                "interested": True,
                "qualified": True,
                "notice_period": "45 days",
                "portfolio": "42 enterprise accounts; INR 18 Cr ARR",
            },
            "is_demo": True,
        }
