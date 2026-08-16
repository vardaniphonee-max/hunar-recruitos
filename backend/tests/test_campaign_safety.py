from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main_module
from app.database import Base, get_db
from app.main import app, apply_call_payload
from app.models import Call, Candidate, Campaign
from app.seed import seed_demo


def test_late_provider_event_cannot_regress_completed_call():
    call = Call(
        campaign_id=1, candidate_id=1, request_id="safe-ordering",
        status="COMPLETED", lifecycle_status="COMPLETED", is_demo=True,
    )
    apply_call_payload(call, {"status": "RINGING", "lifecycle_status": "RINGING"})
    assert call.status == "COMPLETED"
    assert call.lifecycle_status == "COMPLETED"


def test_partial_provider_failure_is_tracked_and_required_agent_data_is_sent(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    with testing_session() as db:
        seed_demo(db)

    captured: list[dict[str, Any]] = []

    class PartialVoiceProvider:
        async def create_call(self, **kwargs: Any) -> dict[str, Any]:
            captured.append(kwargs["custom_data"])
            if len(captured) == 2:
                raise RuntimeError("simulated provider rejection")
            return {
                "id": "tracked-call-1", "request_id": kwargs["request_id"],
                "status": "INITIATED", "lifecycle_status": "INITIATED", "is_demo": True,
            }

    def override_db():
        with testing_session() as db:
            yield db

    monkeypatch.setattr(main_module, "DemoVoiceProvider", PartialVoiceProvider)
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        role_id = client.get("/api/roles").json()[0]["id"]
        client.post(
            "/api/talent/search",
            json={"role_id": role_id, "titles": ["Customer Success Manager"]},
        )
        with testing_session() as db:
            candidate_ids = list(db.scalars(select(Candidate.id).order_by(Candidate.id).limit(2)))

        response = client.post(
            "/api/campaigns",
            json={"role_id": role_id, "name": "Safe partial campaign", "candidate_ids": candidate_ids},
        )
        assert response.status_code == 201
        assert response.json()["status"] == "PARTIAL"
        assert response.json()["failed_call_count"] == 1
        assert {
            "job_title", "job_location", "required_skills", "experience_range",
            "interview_questions", "job_summary", "company_name",
        }.issubset(captured[0])

        with testing_session() as db:
            campaign = db.get(Campaign, response.json()["id"])
            calls = list(db.scalars(select(Call).where(Call.campaign_id == campaign.id)))
        assert campaign.status == "PARTIAL"
        assert len(calls) == 2
        assert {call.status for call in calls} == {"INITIATED", "FAILED"}
        assert all(call.raw_provider_payload for call in calls)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
