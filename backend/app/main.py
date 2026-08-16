import json
import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from hashlib import sha256
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import (
    ActivityEvent, Call, Campaign, Candidate, CandidateRole, Role,
    ScreeningQuestion, SearchRun, StructuredAnswer, WebhookEvent,
)
from .providers.apollo import ApolloPeopleSearchProvider
from .providers.demo import DemoPeopleSearchProvider, DemoVoiceProvider
from .providers.hunar import HunarVoiceProvider
from .schemas import CampaignCreate, ReviewCreate, RoleCreate, SearchCriteria
from .seed import seed_demo
from .webhooks import verify_hunar_webhook_signature, webhook_fingerprint


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if settings.demo_mode:
        with SessionLocal() as db:
            seed_demo(db)
    yield


app = FastAPI(
    title="Hunar RecruitOS API",
    description="Recruiter workflow with Hunar Voice and Apollo provider adapters.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "X-Hunar-Signature", "X-Hunar-Timestamp"],
)

Db = Annotated[Session, Depends(get_db)]
E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
LIFECYCLE_RANK = {
    "NOT_STARTED": 0, "INITIATED": 1, "RINGING": 2, "IN_PROGRESS": 3,
    "COMPLETED": 4, "FAILED": 4, "NO_ANSWER": 4, "CANCELLED": 4,
}
TERMINAL_CALL_STATUSES = {"COMPLETED", "FAILED", "NO_ANSWER", "CANCELLED"}


def apply_call_payload(call: Call, payload: dict[str, Any]) -> None:
    """Merge provider state without allowing late events to regress the lifecycle."""
    current = (call.lifecycle_status or call.status or "NOT_STARTED").upper()
    incoming = str(payload.get("lifecycle_status") or payload.get("status") or current).upper()
    current_rank = LIFECYCLE_RANK.get(current, -1)
    incoming_rank = LIFECYCLE_RANK.get(incoming, current_rank)
    can_advance = current not in TERMINAL_CALL_STATUSES and incoming_rank >= current_rank
    if can_advance or incoming == current:
        call.lifecycle_status = incoming
        call.status = str(payload.get("status") or incoming).upper()
    call.duration_seconds = payload.get("duration_seconds", call.duration_seconds)
    call.recording_url = payload.get("recording_url", call.recording_url)
    call.result = payload.get("result", call.result)
    call.raw_provider_payload = payload


def serialize_role(role: Role) -> dict[str, Any]:
    return {
        "id": role.id, "title": role.title, "description": role.description,
        "location": role.location, "experience_min": role.experience_min,
        "experience_max": role.experience_max, "skills": role.skills,
        "status": role.status,
        "questions": [
            {"id": q.id, "prompt": q.prompt, "result_key": q.result_key, "position": q.position}
            for q in sorted(role.questions, key=lambda item: item.position)
        ],
    }


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "demo_mode": settings.demo_mode}


@app.get("/api/dashboard")
def dashboard(db: Db) -> dict[str, int]:
    return {
        "active_roles": db.scalar(select(func.count()).select_from(Role).where(Role.status == "ACTIVE")) or 0,
        "candidates": db.scalar(select(func.count()).select_from(Candidate)) or 0,
        "calls_initiated": db.scalar(select(func.count()).select_from(Call)) or 0,
        "calls_completed": db.scalar(select(func.count()).select_from(Call).where(Call.status == "COMPLETED")) or 0,
        "qualified": db.scalar(select(func.count()).select_from(CandidateRole).where(CandidateRole.stage == "QUALIFIED")) or 0,
    }


@app.get("/api/roles")
def list_roles(db: Db) -> list[dict[str, Any]]:
    return [serialize_role(role) for role in db.scalars(select(Role).order_by(Role.created_at.desc())).unique()]


@app.post("/api/roles", status_code=status.HTTP_201_CREATED)
def create_role(data: RoleCreate, db: Db) -> dict[str, Any]:
    if data.experience_min > data.experience_max:
        raise HTTPException(422, "experience_min cannot exceed experience_max")
    role = Role(**data.model_dump(exclude={"questions"}))
    db.add(role)
    db.flush()
    for position, question in enumerate(data.questions, start=1):
        db.add(ScreeningQuestion(role_id=role.id, position=position, **question.model_dump()))
    db.commit()
    db.refresh(role)
    return serialize_role(role)


@app.post("/api/talent/search")
async def search_talent(criteria: SearchCriteria, db: Db) -> dict[str, Any]:
    role = db.get(Role, criteria.role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    if settings.demo_mode or not settings.apollo_api_key:
        provider = DemoPeopleSearchProvider()
        provider_name = "demo-apollo"
        is_demo = True
    else:
        provider = ApolloPeopleSearchProvider(settings.apollo_api_key, settings.apollo_base_url)
        provider_name = "apollo"
        is_demo = False
    try:
        results, raw = await provider.search(criteria)
    except Exception as exc:
        raise HTTPException(502, "People-search provider request failed") from exc

    run = SearchRun(
        role_id=role.id, provider=provider_name, is_demo=is_demo,
        criteria=criteria.model_dump(), result_count=len(results), raw_response=raw,
    )
    db.add(run)
    for item in results:
        candidate = db.scalar(select(Candidate).where(
            Candidate.source == item.source, Candidate.external_id == item.external_id
        ))
        if not candidate:
            candidate = Candidate(**item.model_dump(exclude={"match_score", "match_reasons"}))
            db.add(candidate)
            db.flush()
        relation = db.scalar(select(CandidateRole).where(
            CandidateRole.role_id == role.id, CandidateRole.candidate_id == candidate.id
        ))
        if not relation:
            db.add(CandidateRole(
                role_id=role.id, candidate_id=candidate.id, stage="DISCOVERED",
                match_score=item.match_score, match_reasons=item.match_reasons,
            ))
    db.commit()
    return {"provider": provider_name, "is_demo": is_demo, "results": [item.model_dump() for item in results]}


@app.put("/api/roles/{role_id}/candidates/{candidate_id}/shortlist")
def shortlist(role_id: int, candidate_id: int, db: Db) -> dict[str, str]:
    relation = db.scalar(select(CandidateRole).where(
        CandidateRole.role_id == role_id, CandidateRole.candidate_id == candidate_id
    ))
    if not relation:
        raise HTTPException(404, "Candidate is not in this role pipeline")
    relation.stage = "SHORTLISTED"
    db.add(ActivityEvent(kind="candidate_shortlisted", message="Candidate shortlisted", entity_type="candidate", entity_id=candidate_id))
    db.commit()
    return {"stage": relation.stage}


@app.post("/api/campaigns", status_code=status.HTTP_201_CREATED)
async def create_campaign(data: CampaignCreate, db: Db) -> dict[str, Any]:
    role = db.get(Role, data.role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    is_demo = settings.demo_mode or not data.authorized_live_call
    if not is_demo and (not settings.hunar_api_key or not settings.hunar_agent_id):
        raise HTTPException(409, "Live Hunar credentials and agent ID are not configured")
    candidates = list(db.scalars(select(Candidate).where(Candidate.id.in_(data.candidate_ids))))
    if len(candidates) != len(set(data.candidate_ids)):
        raise HTTPException(422, "One or more candidates do not exist")
    if not is_demo:
        invalid_candidates = [
            candidate.name for candidate in candidates
            if not candidate.phone or not E164_PATTERN.fullmatch(candidate.phone)
        ]
        if invalid_candidates:
            names = ", ".join(invalid_candidates[:3])
            raise HTTPException(
                422,
                f"Live outreach requires an authorized E.164 phone number for: {names}",
            )

    campaign = Campaign(role_id=role.id, name=data.name, status="QUEUED", is_demo=is_demo)
    db.add(campaign)
    db.flush()
    provider = DemoVoiceProvider() if is_demo else HunarVoiceProvider(settings.hunar_api_key or "", settings.hunar_base_url)
    callback_config = None
    if not is_demo and settings.public_api_url:
        url = f"{settings.public_api_url.rstrip('/')}/api/webhooks/hunar"
        callback_config = {
            "call_status_callback_url": url,
            "call_recording_callback_url": url,
            "call_result_callback_url": url,
            "call_summary_callback_url": url,
        }

    queued_calls: list[tuple[Candidate, Call]] = []
    for candidate in candidates:
        request_id = f"recruitos-{campaign.id}-{candidate.id}-{uuid4().hex[:8]}"
        call = Call(
            campaign_id=campaign.id, candidate_id=candidate.id,
            request_id=request_id, status="NOT_STARTED", lifecycle_status="NOT_STARTED",
            is_demo=is_demo,
        )
        db.add(call)
        queued_calls.append((candidate, call))
    db.commit()

    question_text = "\n".join(
        f"{index}. {question.prompt}" for index, question in enumerate(
            sorted(role.questions, key=lambda item: item.position), start=1
        )
    )
    custom_data = {
        "job_role": role.title,
        "job_title": role.title,
        "location": role.location,
        "job_location": role.location,
        "required_skills": ", ".join(role.skills),
        "experience_range": f"{role.experience_min}-{role.experience_max} years",
        "interview_questions": question_text,
        "job_summary": role.description,
        "company_name": settings.recruiting_company_name,
    }
    created_calls = []
    failed_calls = 0
    for candidate, call in queued_calls:
        try:
            response = await provider.create_call(
                agent_id=settings.hunar_agent_id or "demo-agent",
                callee_name=candidate.name,
                mobile_number=candidate.phone or "+910000000000",
                custom_data=custom_data,
                request_id=call.request_id,
                callback_config=callback_config,
            )
            call.provider_call_id = response["id"]
            call.request_id = response.get("request_id", call.request_id)
            apply_call_payload(call, response)
            created_calls.append(response)
        except Exception as exc:
            failed_calls += 1
            call.status = "FAILED"
            call.lifecycle_status = "FAILED"
            call.raw_provider_payload = {"error": type(exc).__name__, "tracked": True}
        db.commit()

    campaign.status = "FAILED" if not created_calls else "PARTIAL" if failed_calls else "IN_PROGRESS"
    db.commit()
    if not created_calls:
        raise HTTPException(502, "Voice provider rejected every queued call; failures were recorded")
    return {
        "id": campaign.id, "status": campaign.status, "is_demo": is_demo,
        "calls": created_calls, "failed_call_count": failed_calls,
    }


@app.get("/api/calls/{call_id}")
async def get_call(call_id: int, db: Db) -> dict[str, Any]:
    call = db.get(Call, call_id)
    if not call:
        raise HTTPException(404, "Call not found")
    provider = DemoVoiceProvider() if call.is_demo else HunarVoiceProvider(settings.hunar_api_key or "", settings.hunar_base_url)
    if call.provider_call_id:
        payload = await provider.get_call(call.provider_call_id)
        apply_call_payload(call, payload)
        for key, value in (call.result or {}).items():
            answer = db.scalar(select(StructuredAnswer).where(
                StructuredAnswer.call_id == call.id, StructuredAnswer.key == key
            ))
            if not answer:
                db.add(StructuredAnswer(call_id=call.id, key=key, value=value, source="provider"))
        db.commit()
    return {
        "id": call.id, "provider_call_id": call.provider_call_id, "request_id": call.request_id,
        "status": call.status, "lifecycle_status": call.lifecycle_status,
        "duration_seconds": call.duration_seconds, "recording_url": call.recording_url,
        "result": call.result, "is_demo": call.is_demo,
    }


@app.post("/api/webhooks/hunar")
async def hunar_webhook(
    request: Request, db: Db,
    x_hunar_signature: Annotated[str | None, Header()] = None,
    x_hunar_timestamp: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    raw_body = await request.body()
    if settings.demo_mode and request.headers.get("x-demo-webhook") == "true":
        valid = True
    else:
        valid = verify_hunar_webhook_signature(
            signature_header=x_hunar_signature, timestamp_header=x_hunar_timestamp,
            request_body=raw_body, trusted_api_keys=[settings.hunar_api_key] if settings.hunar_api_key else [],
            tolerance_seconds=settings.webhook_tolerance_seconds,
        )
    if not valid:
        raise HTTPException(401, "Invalid Hunar webhook signature")
    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "Malformed JSON payload") from exc
    if not payload.get("event_type") or not payload.get("call_id"):
        raise HTTPException(422, "event_type and call_id are required")

    fingerprint = webhook_fingerprint(raw_body)
    if db.scalar(select(WebhookEvent).where(WebhookEvent.fingerprint == fingerprint)):
        return {"ok": True, "duplicate": True}
    event = WebhookEvent(
        fingerprint=fingerprint, event_type=payload["event_type"],
        call_id=payload["call_id"], payload=payload,
    )
    db.add(event)
    call = db.scalar(select(Call).where(Call.provider_call_id == payload["call_id"]))
    if call:
        apply_call_payload(call, payload)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"ok": True, "duplicate": True}
    return {"ok": True, "duplicate": False, "event_type": payload["event_type"]}


@app.post("/api/calls/{call_id}/review")
def save_review(call_id: int, data: ReviewCreate, db: Db) -> dict[str, Any]:
    from .models import RecruiterReview
    call = db.get(Call, call_id)
    if not call:
        raise HTTPException(404, "Call not found")
    review = db.scalar(select(RecruiterReview).where(RecruiterReview.call_id == call_id))
    if review:
        review.decision = data.decision
        review.note = data.note
    else:
        review = RecruiterReview(call_id=call_id, **data.model_dump())
        db.add(review)
    db.commit()
    return {"decision": review.decision, "note": review.note}
