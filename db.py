import playhouse.postgres_ext as pw
import os
from dotenv import load_dotenv
from flask_login import UserMixin
from werkzeug.security import check_password_hash

load_dotenv('.env')

database = pw.PostgresqlDatabase(
        os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT')
)


class BaseModel(UserMixin, pw.Model):
    class Meta:
        database = database


class User(BaseModel):
    email = pw.CharField(50, null=False, unique=True)
    password = pw.CharField(300, null=False)
    number = pw.CharField(11, null=False)

    def authenticate(self, password):
        if check_password_hash(self.password, password):
            return True
        return False


class Goods(BaseModel):
    name = pw.CharField(50, null=False, unique=True)


class Group(BaseModel):
    name = pw.CharField(50, null=False)
    user = pw.ForeignKeyField(User, null=False)


class Controller(BaseModel):
    id = pw.UUIDField(primary_key=True)
    user = pw.ForeignKeyField(User, null=False)
    goods = pw.ForeignKeyField(Goods, null=False)
    group = pw.ForeignKeyField(Group, null=True, default=None, on_delete='SET NULL')
    settings = pw.TextField()


class Statistic(BaseModel):
    controller = pw.ForeignKeyField(Controller, null=False, on_delete='CASCADE')
    stats = pw.IntegerField(null=False)
    timing = pw.DateTimeField(null=False)


with database:
    database.create_tables([User, Goods, Group, Controller, Statistic])
    Goods.get_or_create(id=1, name='Термометр')
    Goods.get_or_create(id=2, name='Датчик света')
    Goods.get_or_create(id=3, name='Датчик влажности')
