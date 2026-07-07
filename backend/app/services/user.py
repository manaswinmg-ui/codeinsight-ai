from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository, user_repository
from app.services.base import BaseService


class UserService(BaseService[UserRepository]):
    def __init__(self) -> None:
        super().__init__(user_repository)

    async def get_user(self, db: AsyncSession, user_id: int) -> User | None:
        return await self.repository.get(db, user_id)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await self.repository.get_by_email(db, email)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        return await self.repository.get_by_username(db, username)


user_service = UserService()
