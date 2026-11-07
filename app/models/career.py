from typing import Optional

from sqlmodel import Field, SQLModel


class Career(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True)
    summary: str
    entry_level_note: str
    salary_band: str
    progression: str
