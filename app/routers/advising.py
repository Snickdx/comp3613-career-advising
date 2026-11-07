"""Career-advising scenario JSON API (OpenAPI /docs)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.services import advising
from app.services import advising_auth as auth

router = APIRouter(tags=["career-advising"])


class LoginBody(BaseModel):
    email: str
    password: str


class ProfileBody(BaseModel):
    programme: str
    audience: str = "university"
    courses: str
    interests: str = ""


class CareerFirstBody(BaseModel):
    career_id: int


def _actor_id(x_user_id: str | None) -> int:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        return int(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-User-Id must be int") from exc


@router.post("/auth/login")
def login(body: LoginBody) -> dict[str, Any]:
    user = auth.login(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"user": user}


@router.put("/profile")
def put_profile(
    body: ProfileBody, x_user_id: str | None = Header(default=None)
) -> dict[str, Any]:
    result = advising.upsert_profile(
        _actor_id(x_user_id),
        programme=body.programme,
        audience=body.audience,
        courses=body.courses,
        interests=body.interests,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/profile")
def get_profile(x_user_id: str | None = Header(default=None)) -> dict[str, Any]:
    profile = advising.get_profile(_actor_id(x_user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="no profile")
    return {"profile": profile}


@router.get("/careers")
def careers() -> dict[str, Any]:
    return {"careers": advising.list_careers()}


@router.post("/explore/career-first")
def career_first(
    body: CareerFirstBody, x_user_id: str | None = Header(default=None)
) -> dict[str, Any]:
    result = advising.run_career_first(_actor_id(x_user_id), body.career_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/explore/course-first")
def course_first(x_user_id: str | None = Header(default=None)) -> dict[str, Any]:
    result = advising.run_course_first(_actor_id(x_user_id))
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/gaps/{career_id}")
def gaps(
    career_id: int, x_user_id: str | None = Header(default=None)
) -> dict[str, Any]:
    result = advising.identify_gaps(_actor_id(x_user_id), career_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
