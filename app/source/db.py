from peewee import (
    Model,
    PostgresqlDatabase,
    DateTimeField,
    AutoField,
    CharField,
    TextField,
    ForeignKeyField,
    IntegerField,
    DateTimeField,
    BooleanField,
    )


connection = PostgresqlDatabase('camelot', user='camelot', password='camelot',
                                               host='db', port=5432)

def close_connection():
    connection.close()

class BaseModel(Model):
    class Meta:
        database = connection


class User(BaseModel):
    class Meta:
        db_table = 'camelot_users'

    id = AutoField()
    name = CharField()
    slack_id = CharField()
    is_bot = BooleanField()
    is_deleted = BooleanField()


class Category(BaseModel):
    class Meta:
        db_table = 'camelot_categories'

    id = AutoField()
    name = CharField()
    display_name = CharField()
    description = TextField()
    # True if the 'winning' value must be greater than the current.
    compare_greater = BooleanField()


class GloryWall(BaseModel):
    class Meta:
        db_table = 'camelot_glory_walls'

    id = AutoField()
    full_summary_text = TextField()
    category = ForeignKeyField(Category, backref="glory_walls")
    user = ForeignKeyField(User)
    value = IntegerField()
    timestamp = DateTimeField()
