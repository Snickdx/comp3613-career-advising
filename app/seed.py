"""Seed advisor/student, careers, and course requirements for career-advising."""

from __future__ import annotations

from sqlmodel import Session, select

from app.database import drop_all, ensure_db_and_tables, engine
from app.models.career import Career
from app.models.career_course import CareerCourse
from app.models.profile import Profile
from app.models.user import User
from app.utilities.security import encrypt_password

USERS = [
    # username, email, password, role
    ("advisor", "advisor@example.com", "adv-dev", "advisor"),
    ("student", "student@example.com", "stud-dev", "student"),
]

CAREERS = [
    (
        "Software Developer",
        "Build applications and services.",
        "Junior roles emphasize fundamentals and teamwork.",
        "TTD 8k-14k entry (illustrative)",
        "Mid → senior → lead over several years",
    ),
    (
        "Data Analyst",
        "Analyze data to support decisions.",
        "Entry roles often need SQL and stats basics.",
        "TTD 7k-12k entry (illustrative)",
        "Analyst → senior analyst → analytics lead",
    ),
    (
        "Network Engineer",
        "Design and operate networks.",
        "Entry roles start with ops/support exposure.",
        "TTD 7k-13k entry (illustrative)",
        "Engineer → senior → architect",
    ),
]

REQUIREMENTS = [
    # career title, course code, required
    ("Software Developer", "COMP1601", 1),
    ("Software Developer", "COMP1602", 1),
    ("Software Developer", "COMP2601", 1),
    ("Software Developer", "COMP3613", 0),
    ("Data Analyst", "COMP1601", 1),
    ("Data Analyst", "MATH1115", 1),
    ("Data Analyst", "COMP2605", 1),
    ("Network Engineer", "COMP1601", 1),
    ("Network Engineer", "COMP2501", 1),
]


def seed(*, reset: bool = False) -> None:
    import app.models  # noqa: F401

    if reset:
        try:
            drop_all()
        except Exception:
            pass
    ensure_db_and_tables()

    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing and not reset:
            return

        for username, email, password, role in USERS:
            session.add(
                User(
                    username=username,
                    email=email,
                    password=encrypt_password(password),
                    role=role,
                )
            )
        session.commit()

        student = session.exec(
            select(User).where(User.email == "student@example.com")
        ).one()
        session.add(
            Profile(
                user_id=student.id,
                programme="BSc Computer Science",
                audience="university",
                courses="COMP1601,COMP1602,MATH1115",
                interests="software,data",
            )
        )

        for title, summary, entry, salary, progression in CAREERS:
            session.add(
                Career(
                    title=title,
                    summary=summary,
                    entry_level_note=entry,
                    salary_band=salary,
                    progression=progression,
                )
            )
        session.commit()

        by_title = {c.title: c.id for c in session.exec(select(Career)).all()}
        for title, code, required in REQUIREMENTS:
            session.add(
                CareerCourse(
                    career_id=by_title[title], course_code=code, required=required
                )
            )
        session.commit()
