from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Candidate, CandidateRole, Role, ScreeningQuestion


QUESTIONS = [
    ("enterprise_portfolio", "Tell me about the largest portfolio of enterprise accounts you have managed."),
    ("churn_risk", "How do you identify and respond to churn risk?"),
    ("hybrid_work", "Are you comfortable working from Bengaluru three days a week?"),
    ("availability", "What is your notice period and expected compensation?"),
]


def seed_demo(db: Session) -> Role:
    existing = db.scalar(select(Role).where(Role.title == "Customer Success Manager"))
    if existing:
        return existing
    role = Role(
        title="Customer Success Manager",
        description="Own a portfolio of enterprise customers, drive onboarding and adoption, identify churn risk, and partner across teams to deliver measurable outcomes.",
        location="Bengaluru, India",
        experience_min=5,
        experience_max=8,
        skills=["B2B SaaS", "Enterprise accounts", "Retention"],
    )
    db.add(role)
    db.flush()
    for position, (key, prompt) in enumerate(QUESTIONS, start=1):
        db.add(ScreeningQuestion(role_id=role.id, prompt=prompt, result_key=key, position=position))

    candidate_rows = [
        ("demo-ananya", "Ananya Rao", "Senior Customer Success Manager", "Chargebee", "Bengaluru, India", 7, 94),
        ("demo-rohan", "Rohan Mehta", "Customer Success Lead", "Freshworks", "Chennai, India", 6, 89),
    ]
    for external_id, name, title, company, location, years, score in candidate_rows:
        candidate = Candidate(
            external_id=external_id, source="demo-apollo", is_demo=True, name=name,
            title=title, company=company, location=location, experience_years=years,
            skills=["B2B SaaS", "Enterprise accounts"],
        )
        db.add(candidate)
        db.flush()
        db.add(CandidateRole(
            role_id=role.id, candidate_id=candidate.id, stage="SHORTLISTED",
            match_score=score, match_reasons=["Title alignment", "Relevant experience"],
        ))
    db.commit()
    db.refresh(role)
    return role
