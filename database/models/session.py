from sqlalchemy import Column, String, BigInteger, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .BASE import Base


DEFAULT_SITES = [
    {
        "name": "Лента 🇷🇺",
        "url": "https://lenta.ru/parts/news/",
        "tag": "h3",
        "base_url": "https://lenta.ru"
    },
    {
        "name": "BBC 🇬🇧",
        "url": "https://www.bbc.com/news",
        "tag": "h2",
        "base_url": "https://www.bbc.com"
    },
    {
        "name": "Настоящее время 🇷🇺",
        "url": "https://www.currenttime.tv/news",
        "tag": "h4",
        "base_url": "https://www.currenttime.tv"
    },
    {
        "name": "NY Times 🇺🇸",
        "url": "https://www.nytimes.com/",
        "tag": "p",
        "class": "indicate-hover",
        "base_url": "https://www.nytimes.com"
    }
]


class Site(Base):
    __tablename__ = 'sites'

    id = Column(BigInteger, primary_key=True)
    session_id = Column(BigInteger, ForeignKey('session.id'))
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    tag = Column(String(50), nullable=False)
    base_url = Column(String(500), nullable=False)
    news = Column(JSON, nullable=False, default=[])

    def __repr__(self):
        return f"<Site(id={self.id}, name='{self.name}', news_count={len(self.news)})>"


class Session(Base):
    __tablename__ = 'session'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=False)

    sites = relationship("Site", backref="session", cascade="all, delete-orphan")

    @classmethod
    def create_with_default_sites(cls, db, user_id):
        """Создает сессию с сайтами (новости пустые)"""
        session = cls(user_id=user_id, is_active=True)
        db.add(session)
        db.flush()  # Получаем ID сессии

        for site_data in DEFAULT_SITES:
            site = Site(
                session_id=session.id,
                name=site_data['name'],
                url=site_data['url'],
                tag=site_data['tag'],
                base_url=site_data['base_url'],
                news=[]
            )
            db.add(site)

        db.commit()
        return session