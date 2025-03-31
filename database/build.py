from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import create_database, drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_config
from database.models import Base, Session, Site
from database.models.session import DEFAULT_SITES


def init():
    #for docker
    '''proceed = input('Do you want to rebuild and wipe db? ("REBUILD" if yes) ')
    if proceed != 'REBUILD':
        return'''

    engine = create_engine(
        f"postgresql://{db_config.username}:{db_config.password}@"
        f"{db_config.host}/{db_config.database}"
    )
    SessionLocal = sessionmaker(bind=engine)

    try:
        drop_database(engine.url)
    except OperationalError:
        pass

    create_database(engine.url)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        session = Session(user_id=1, is_active=True)
        db.add(session)
        db.flush()

        for site_data in DEFAULT_SITES:
            site = Site(
                session_id=session.id,
                name=site_data["name"],
                url=site_data["url"],
                tag=site_data["tag"],
                base_url=site_data["base_url"],
                news=[]
            )
            if "class" in site_data:
                site.class_ = site_data["class"]
            db.add(site)

        db.commit()
        print(f"Added {len(DEFAULT_SITES)}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


def soft_init():
    engine = create_engine(
        f"postgresql://{db_config.username}:{db_config.password}@"
        f"{db_config.host}/{db_config.database}"
    )
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        Base.metadata.create_all(bind=engine)

        if db.query(Site).count() == 0:
            session = Session(user_id=1, is_active=True)
            db.add(session)
            db.flush()

            for site_data in DEFAULT_SITES:
                site = Site(
                    session_id=session.id,
                    name=site_data["name"],
                    url=site_data["url"],
                    tag=site_data["tag"],
                    base_url=site_data["base_url"],
                    news=[]
                )
                if "class" in site_data:
                    site.class_ = site_data["class"]
                db.add(site)

            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    init()
