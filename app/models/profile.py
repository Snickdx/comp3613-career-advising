from typing import Optional

from sqlmodel import Field, SQLModel


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, unique=True)
    programme: str
    audience: str
    courses: str
    interests: str = ""
