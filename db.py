import uuid

import databases
import ormar
import sqlalchemy
from pydantic import HttpUrl

DATABASE_URL = "sqlite:///db.sqlite"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Users(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'users'

    tg_user_id: int = ormar.Integer(primary_key=True)
    is_active: bool = ormar.Boolean(default=True)


class Products(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'products'

    id: int = ormar.Integer(primary_key=True)
    product_url: HttpUrl = ormar.String(max_length=2083)
    product_name: str = ormar.String(max_length=256)
    desired_price: int = ormar.String(max_length=16)
    task_id: str = ormar.String(max_length=128)
    tg_user_id: Users = ormar.ForeignKey(Users)
    is_active: bool = ormar.Boolean(default=True)


# class Tasks(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = 'tasks'
#
#     product_url: int = ormar.Integer(primary_key=True)
#     tg_user_id: Users = ormar.ForeignKey(Users)
#     task_id: int = ormar.Integer()
#     is_active: bool = ormar.Boolean(default=True)
