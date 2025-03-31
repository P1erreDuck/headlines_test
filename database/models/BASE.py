from sqlalchemy.orm import declarative_base
from config import bot_config

Base = declarative_base(name=bot_config.project)