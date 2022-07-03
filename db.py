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


class Cities(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'cities'

    id: int = ormar.Integer(primary_key=True)
    city_name: str = ormar.String(max_length=64, default='Москва')
    city_code: str = ormar.String(max_length=128, default='?action=changeCity&space=msk_cl:')


class Users(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'users'

    tg_user_id: int = ormar.Integer(primary_key=True)
    is_active: bool = ormar.Boolean(default=True)
    city: Cities = ormar.ForeignKey(Cities, nullabe=False, related_name='user')


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

