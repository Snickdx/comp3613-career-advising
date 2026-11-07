"""
Exploration pipelines — intended Template Method seam, copy-pasted poorly.

Both modes should share one algorithm skeleton:
  load profile → match → rank (non-absolute) → identify course gaps → present

Instead this file duplicates nearly the same steps in two functions with
inconsistent hooks (absolute wording in one path, gap-check skipped in another,
high-school audience still served).

Ideal fix: abstract template method `run()` with hooks
`match()`, `rank()`, `identify_gaps()`, `present()` for CareerFirst /
CourseFirst subclasses (or equivalent).
"""

from __future__ import annotations

from typing import Any


def explore_career_first(
    *,
    profile: dict[str, Any],
    careers: list[dict[str, Any]],
    requirements: dict[int, list[dict[str, Any]]],
    target_career_id: int,
) -> dict[str, Any]:
    # Step 1 — load (already passed in)
    audience = profile.get("audience") or "university"
    courses = _split(profile.get("courses"))

    # DEFECT: high-school audience still fully served
    _ = audience

    career = next((c for c in careers if c["id"] == target_career_id), None)
    if career is None:
        return {"ok": False, "error": "career not found"}

    reqs = requirements.get(target_career_id, [])
    required_codes = [r["course_code"] for r in reqs if r.get("required")]
    have = set(courses)
    missing = [c for c in required_codes if c not in have]

    # Step — rank: DEFECT returns a single forced career as "the path"
    ranking = [
        {
            "career_id": career["id"],
            "title": career["title"],
            "score": 1.0,
            "wording": f"You should pursue {career['title']}.",  # absolute
            "entry_level_note": career["entry_level_note"],
            "salary_band": career["salary_band"],
            "progression": career["progression"],
        }
    ]

    # Step — gaps included here
    return {
        "ok": True,
        "mode": "career_first",
        "recommendations": ranking,
        "related_courses": required_codes,
        "missing_courses": missing,
        "enrol_hint": "Register for missing courses in Banner.",  # DEFECT: enrol sneak-in
    }


def explore_course_first(
    *,
    profile: dict[str, Any],
    careers: list[dict[str, Any]],
    requirements: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    # Near-duplicate skeleton with different bugs
    audience = profile.get("audience") or "university"
    courses = _split(profile.get("courses"))
    interests = _split(profile.get("interests"))

    if audience == "high_school":
        # DEFECT: special-cases HS instead of rejecting out-of-scope
        courses = courses + interests

    scored: list[dict[str, Any]] = []
    for career in careers:
        reqs = requirements.get(career["id"], [])
        codes = [r["course_code"] for r in reqs]
        overlap = len(set(codes) & set(courses))
        score = overlap / max(len(codes), 1)
        # DEFECT: interests ignored in scoring unless HS branch above
        scored.append(
            {
                "career_id": career["id"],
                "title": career["title"],
                "score": score,
                "wording": f"Suited option: {career['title']} (not a requirement).",
                "entry_level_note": career["entry_level_note"],
                "salary_band": career["salary_band"],
                "progression": career["progression"],
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    # DEFECT: if top score is unique and 1.0, wording flips to absolute
    if scored and scored[0]["score"] >= 1.0:
        scored[0]["wording"] = f"This is your career: {scored[0]['title']}."

    # DEFECT: gap identification skipped entirely in course-first path
    return {
        "ok": True,
        "mode": "course_first",
        "recommendations": scored,
        "related_courses": courses,
        "missing_courses": [],
    }


def _split(raw: str | None) -> list[str]:
    return [p.strip() for p in (raw or "").split(",") if p.strip()]
