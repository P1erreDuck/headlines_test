from sqlalchemy import Column, String, BigInteger, JSON
from sqlalchemy.orm import relationship
from .BASE import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    full_name = Column(String(64), nullable=False)
    username = Column(String(64), nullable=True)

    # Подписки в формате ["Лента", "BBC"]
    subscriptions = Column(JSON, nullable=False, default=[])

    async def update_subscriptions(self, session, new_subscriptions):
        """Обновляет список подписок и сохраняет в БД"""
        self.subscriptions = new_subscriptions
        session.add(self)
        await session.commit()
        return self