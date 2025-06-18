from sqlalchemy import select

from app.authentication.models import User
from app.base.test import BaseTest


class AuthenticationBaseTest(BaseTest):
    async def get_user(self, email: str):
        query = select(User).where(User.email == email)
        user = await self.session.scalar(query)
        self.assertIsNotNone(user)
        return user
