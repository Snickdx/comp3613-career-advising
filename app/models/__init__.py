"""SQLModel table registry.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.career import Career
from app.models.career_course import CareerCourse
from app.models.profile import Profile
from app.models.user import User

__all__ = [
    "User",
    "Profile",
    "Career",
    "CareerCourse",
]
