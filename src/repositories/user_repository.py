import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repositories.base import BaseRepository
from src.schemas.user import UserCreate

logger = logging.getLogger("uvicorn.error")


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(self.model).where(User.username == username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            **user_data.model_dump(exclude_unset=True, exclude={"password"}),
            hash_password=hashed_password,
        )
        return await self.create(user)
