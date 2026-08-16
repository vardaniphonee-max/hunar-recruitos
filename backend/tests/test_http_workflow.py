from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Call, Candidate, CandidateRole, Role
from app.seed import seed_demo


def test_demo_http_workflow_and_webhook_idempotency():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    with testing_session() as db:
        seed_demo(db)

    def override_db():
        with testing_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "demo_mode": True}

        roles = client.get("/api/roles")
        assert roles.status_code == 200
        role_id = roles.json()[0]["id"]

        invalid_role = client.post(
            "/api/roles",
            json={
                "title": "Customer Success Manager",
                "description": "A sufficiently detailed role description for validation.",
                "location": "Bengaluru",
                "experience_min": 8,
                "experience_max": 5,
                "skills": ["SaaS"],
                "questions": [{"prompt": "Tell me about your customer portfolio.", "result_key": "portfolio"}],
            },
        )
        assert invalid_role.status_code == 422
        assert invalid_role.json()["detail"] == "experience_min cannot exceed experience_max"

        search_payload = {
            "role_id": role_id,
            "titles": ["Customer Success Manager"],
            "locations": ["Bengaluru"],
            "keywords": ["SaaS"],
            "page": 1,
            "per_page": 10,
        }
        first_search = client.post("/api/talent/search", json=search_payload)
        second_search = client.post("/api/talent/search", json=search_payload)
        assert first_search.status_code == second_search.status_code == 200
        assert first_search.json()["provider"] == "demo-apollo"
        assert first_search.json()["is_demo"] is True
        assert len(first_search.json()["results"]) == 4

        with testing_session() as db:
            candidate_count = db.scalar(select(func.count()).select_from(Candidate))
            relation_count = db.scalar(
                select(func.count()).select_from(CandidateRole).where(CandidateRole.role_id == role_id)
            )
            candidate_ids = list(db.scalars(select(Candidate.id).order_by(Candidate.id).limit(2)))
        assert candidate_count == 4
        assert relation_count == 4

        shortlist = client.put(f"/api/roles/{role_id}/candidates/{candidate_ids[0]}/shortlist")
        assert shortlist.status_code == 200
        assert shortlist.json() == {"stage": "SHORTLISTED"}

        missing_candidate = client.post(
            "/api/campaigns",
            json={"role_id": role_id, "name": "August outreach", "candidate_ids": [999999]},
        )
        assert missing_candidate.status_code == 422

        campaign = client.post(
            "/api/campaigns",
            json={"role_id": role_id, "name": "August outreach", "candidate_ids": candidate_ids},
        )
        assert campaign.status_code == 201
        assert campaign.json()["is_demo"] is True
        assert len(campaign.json()["calls"]) == 2

        with testing_session() as db:
            call = db.scalar(select(Call).where(Call.campaign_id == campaign.json()["id"]).order_by(Call.id))
        assert call is not None

        call_result = client.get(f"/api/calls/{call.id}")
        assert call_result.status_code == 200
        assert call_result.json()["is_demo"] is True

        review = client.post(
            f"/api/calls/{call.id}/review",
            json={"decision": "Hold for review", "note": "Confirm notice period."},
        )
        assert review.status_code == 200
        assert review.json()["decision"] == "Hold for review"

        unsigned = client.post(
            "/api/webhooks/hunar",
            json={"event_type": "call_summary", "call_id": call.provider_call_id},
        )
        assert unsigned.status_code == 401

        payload = {
            "event_type": "call_summary",
            "call_id": call.provider_call_id,
            "status": "COMPLETED",
        }
        first_webhook = client.post("/api/webhooks/hunar", json=payload, headers={"x-demo-webhook": "true"})
        repeated_webhook = client.post(
            "/api/webhooks/hunar",
            content=(
                '{ "status": "COMPLETED", "call_id": "'
                + str(call.provider_call_id)
                + '", "event_type": "call_summary" }'
            ),
            headers={"x-demo-webhook": "true", "content-type": "application/json"},
        )
        assert first_webhook.status_code == repeated_webhook.status_code == 200
        assert first_webhook.json()["duplicate"] is False
        assert repeated_webhook.json()["duplicate"] is True
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
