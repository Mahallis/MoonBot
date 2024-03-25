from datetime import date
from collections import namedtuple
from peewee import (
    Model,
    DateField,
    TextField,
    PostgresqlDatabase,
    IntegerField,
    CharField,
    ModelSelect
)

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db = PostgresqlDatabase(
    os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)


class BaseModel(Model):

    def create_tables(self) -> None:
        tables_names: list = ['MoonData', 'MoonUser']
        db.create_tables(tables_names)

    class Meta:
        database = db


class MoonData(BaseModel):
    '''This class describes a model for storing data about moon
    from 1980 to 2030.'''

    date = DateField(null=False)
    header = CharField(max_length=50, null=False)
    text = TextField(null=False)

    def get_moon_data(self) -> dict:
        '''Gets information from a database and converts it to a dict
        where id is a key and header and text are values'''

        MoonItem = namedtuple('MoonItem', ['header', 'text'])
        today_info = self.select().where(MoonData.date == date.today())
        return {
            str(item.id): MoonItem(item.header, item.text)
            for item in today_info}


class MoonUser(BaseModel):
    '''This class describes a model for storing data about user
    notification time'''

    user_id = IntegerField(unique=True, null=False)
    notify_time = TextField(null=False)

    def set_user_time(self, user_id, user_time) -> None:
        if user := self.get_or_none(MoonUser.user_id == user_id):
            user.notify_time = user_time
            user.save()
        else:
            MoonUser(user_id=user_id, notify_time=user_time).save()

    def get_user_time(self, user_id) -> str:
        if user := self.get_or_none(MoonUser.user_id == user_id):
            return user.notify_time
        return ''

    def get_all_users(self) -> ModelSelect:
        return self.select()
