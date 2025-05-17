import asyncio

import asyncpg
from gino.schema import GinoSchemaVisitor
from gino import Gino
from sqlalchemy import Column, sql, BigInteger, DateTime
from data.config import POSTGRES_URI

db = Gino()


async def create_db():
    await db.set_bind(POSTGRES_URI)
    db.gino: GinoSchemaVisitor
    # если нужно почистить все таблицы
    # await db.gino.drop_all()
    try:
        await db.gino.create()
    except asyncpg.exceptions.DuplicateTableError:
        pass


loop = asyncio.get_event_loop()


class OpenDays(db.Model):
    __tablename__ = 'opendays'
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    day = Column(db.Integer)
    month = Column(db.Integer)
    year = Column(db.Integer)
    available = Column(db.Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=db.func.now())


class OpenHours(db.Model):
    __tablename__ = 'openhours'
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    date = Column(db.String)
    start_hour = Column(db.String)
    description = Column(db.Text, default=None)
    comment = Column(db.Text, default=None)
    reserved = Column(db.Boolean, default=False)
    user_reserved = Column(db.BigInteger, default=None)
    created_at = Column(DateTime(timezone=True), server_default=db.func.now())


class Users(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    user_id = Column(db.BigInteger)
    first_name = Column(db.String)
    last_name = Column(db.String)
    login = Column(db.String)
    contact = Column(db.String)
    comment = Column(db.Text)
    discount = Column(db.Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=db.func.now())


class History(db.Model):
    __tablename__ = "history"
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    user_id = Column(db.BigInteger)
    date = Column(db.String)
    start_hour = Column(db.String)
    description = Column(db.Text, default=None)
    comment = Column(db.Text, default=None)
    created_at = Column(DateTime(timezone=True), server_default=db.func.now())


loop.run_until_complete(create_db())
