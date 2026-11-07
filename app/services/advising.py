"""Profiles and exploration entry points."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models.career import Career
from app.models.career_course import CareerCourse
from app.models.profile import Profile
from app.services import exploration
from app.services.advising_auth import get_user


def upsert_profile(
    user_id: int,
    *,
    programme: str,
    audience: str,
    courses: str,
    interests: str = "",
) -> dict[str, Any]:
    user = get_user(user_id)
    if not user or user["role"] not in {"student", "advisor"}:
        return {"ok": False, "error": "student/advisor only"}
    # DEFECT: audience=high_school accepted

    with Session(engine) as session:
        profile = session.exec(
            select(Profile).where(Profile.user_id == user_id)
        ).one_or_none()
        if profile:
            profile.programme = programme
            profile.audience = audience
            profile.courses = courses
            profile.interests = interests
        else:
            profile = Profile(
                user_id=user_id,
                programme=programme,
                audience=audience,
                courses=courses,
                interests=interests,
            )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return {"ok": True, "profile": profile.model_dump()}


def get_profile(user_id: int) -> dict[str, Any] | None:
    with Session(engine) as session:
        row = session.exec(
            select(Profile).where(Profile.user_id == user_id)
        ).one_or_none()
        return row.model_dump() if row else None


def list_careers() -> list[dict[str, Any]]:
    with Session(engine) as session:
        rows = session.exec(select(Career).order_by(Career.id)).all()
        return [r.model_dump() for r in rows]


def _requirements_map(session: Session) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for r in session.exec(select(CareerCourse)).all():
        out.setdefault(r.career_id, []).append(r.model_dump())
    return out


def run_career_first(user_id: int, career_id: int) -> dict[str, Any]:
    profile = get_profile(user_id)
    if not profile:
        return {"ok": False, "error": "create a profile first"}
    with Session(engine) as session:
        careers = [c.model_dump() for c in session.exec(select(Career)).all()]
        reqs = _requirements_map(session)
    return exploration.explore_career_first(
        profile=profile,
        careers=careers,
        requirements=reqs,
        target_career_id=career_id,
    )


def run_course_first(user_id: int) -> dict[str, Any]:
    profile = get_profile(user_id)
    if not profile:
        return {"ok": False, "error": "create a profile first"}
    with Session(engine) as session:
        careers = [c.model_dump() for c in session.exec(select(Career)).all()]
        reqs = _requirements_map(session)
    return exploration.explore_course_first(
        profile=profile,
        careers=careers,
        requirements=reqs,
    )


def identify_gaps(user_id: int, career_id: int) -> dict[str, Any]:
    """Standalone gap check — inconsistent with explore pipelines."""
    profile = get_profile(user_id)
    if not profile:
        return {"ok": False, "error": "create a profile first"}
    with Session(engine) as session:
        reqs = _requirements_map(session).get(career_id, [])
    have = {c.strip() for c in (profile.get("courses") or "").split(",") if c.strip()}
    missing = [r["course_code"] for r in reqs if r["required"] and r["course_code"] not in have]
    return {
        "ok": True,
        "career_id": career_id,
        "missing_courses": missing,
        # DEFECT: also suggests how to obtain
        "next_step": "Contact faculty office to enrol in missing courses.",
    }
