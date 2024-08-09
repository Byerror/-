import peewee
from peewee import *
from decimal import *
from playhouse.migrate import *

def add_comission_profit_field():
    db = peewee.SqliteDatabase('database.sqlite')
    migrator = SqliteMigrator(db)
    migrate(
        migrator.add_column('game', 'comission_profit', peewee.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2))
    )

if __name__ == '__main__':
    add_comission_profit_field()
    input("Success")
