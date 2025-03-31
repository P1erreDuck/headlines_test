from sqlalchemy import create_engine, select, update as upd, insert as ins, delete as dlt
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


class Client:
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        name: str
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.name = name


        self.engine = create_engine(
            self.engine_string(),
            pool_size=50,
            max_overflow=100
        )


        self.async_engine = create_async_engine(
            self.engine_string(async_engine=True),
            pool_size=50,
            max_overflow=100
        )

        # Сессии
        self.Session = sessionmaker(bind=self.engine)
        self.AsyncSession = sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    def engine_string(self, async_engine: bool = False):
        return "postgresql+{}://{}:{}@{}/{}".format(
            "asyncpg" if async_engine else "psycopg2",
            self.username,
            self.password,
            self.host,
            self.name
        )

    async def get(
            self,
            table,
            key=None,
            where=None,
            offset=None,
            order_by=None,
            limit=None,
            get_type='scalar',
            relationships=None
    ):
        async with self.AsyncSession.begin() as session:
            stmt = select(table)
            if where is not None:
                stmt = stmt.where(where)
            if key is not None:
                stmt = stmt.filter_by(**key)
            if offset is not None:
                stmt = stmt.offset(offset)
            if order_by is not None:
                stmt = stmt.order_by(order_by)
            if limit is not None:
                stmt = stmt.limit(limit)
            if relationships:
                for relationship in relationships:
                    path = relationship.split('.')
                    if len(path) > 1:
                        rel, nested_rel = path
                        stmt = stmt.options(joinedload(rel).joinedload(nested_rel))
                    else:
                        stmt = stmt.options(joinedload(relationship))
            result = await getattr(session, get_type)(stmt)
            return result.all() if get_type == 'scalars' else result

    async def update(self, table, key, **kwargs):
        async with self.AsyncSession.begin() as session:
            await session.execute(
                upd(table).values(**kwargs).filter_by(**key)
            )
            await session.commit()

    async def delete(self, table, key):
        async with self.AsyncSession.begin() as session:
            await session.execute(
                dlt(table).filter_by(**key)
            )

    async def insert(self, table, **kwargs):
        async with self.AsyncSession.begin() as session:
            inserted = await session.execute(
                ins(table).values(**kwargs)
            )
            return inserted.inserted_primary_key[0]

    def sync_get(self, table, key=None, get_type='scalar'):
        with self.Session.begin() as session:
            stmt = select(table)
            if key:
                stmt = stmt.filter_by(**key)
            result = getattr(session, get_type)(stmt)
            return result.all() if get_type == 'scalars' else result

    def sync_update(self, table, key, **kwargs):
        with self.Session.begin() as session:
            session.execute(
                upd(table).values(**kwargs).filter_by(**key)
            )

    def sync_delete(self, table, key):
        with self.Session.begin() as session:
            session.execute(
                dlt(table).filter_by(**key)
            )

    def sync_insert(self, table, **kwargs):
        with self.Session.begin() as session:
            inserted = session.execute(
                ins(table).values(**kwargs)
            )
            return inserted.inserted_primary_key[0]