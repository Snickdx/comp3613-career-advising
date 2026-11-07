from sqlmodel import Field, SQLModel


class CareerCourse(SQLModel, table=True):
    career_id: int = Field(primary_key=True, foreign_key="career.id")
    course_code: str = Field(primary_key=True)
    required: int = 1
