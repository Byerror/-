import decimal
import json
from peewee import *
from datetime import datetime, timedelta

db = SqliteDatabase("database.sqlite")


class User(Model):
    user_id = IntegerField(
        null=False,
        unique=True
    )
    balance: decimal.Decimal = DecimalField(
        default=0.0,
        decimal_places=1,
        auto_round=True,
        null=False
    )
    referral_id = ForeignKeyField(
        "self",
        user_id,
        default=None,
        null=True
    )
    timestamp = DateTimeField(default=datetime.now)
    is_withdrawing = BooleanField(default=False)  # Add this field

    class Meta:
        db_column = "games"
        database = db

class Queue(Model):
    id = AutoField()
    user_id = IntegerField()
    data = TextField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db

def add_to_queue(user_id: int, data: dict):
    Queue.create(user_id=user_id, data=json.dumps(data))

def get_queue() -> list[Queue]:
    return Queue.select()

def delete_from_queue(queue_id: int):
    queue_item = Queue.get_by_id(queue_id)
    queue_item.delete_instance()



class Game(Model):
    id = AutoField()
    user = ForeignKeyField(
        User,
        User.user_id
    )
    name = CharField(
        max_length=255,
        null=False
    )
    bid = FloatField(
        null=False
    )
    comment = CharField(
        null=False
    )
    status = IntegerField(
        null=False,
        default=0
    )
    comission_profit = DecimalField(
        null=False,
        default=decimal.Decimal('0.00'),
        max_digits=10,
        decimal_places=2
    )  # Новое поле для хранения комиссии при ничье
    timestamp = DateTimeField(default=datetime.now)
    
    class Meta:
        db_table = "game"
        database = db

class Withdrawal(Model):
    id = AutoField()
    user_id = IntegerField()
    amount = DecimalField(max_digits=10, decimal_places=2)
    timestamp = DateTimeField(default=datetime.now)
    status = CharField(max_length=20, default="pending")

    class Meta:
        database = db


def create_withdrawal(user_id: int, amount: float):
    return Withdrawal.create(user_id=user_id, amount=amount)

def get_withdrawals() -> list[Withdrawal]:
    return Withdrawal.select()

def update_withdrawal_status(withdrawal_id: int, status: str):
    withdrawal = Withdrawal.get_by_id(withdrawal_id)
    withdrawal.status = status
    withdrawal.save()


def create_game(
        user_id: User, 
        name: str, 
        bid: float, 
        comment: str,
        status: int,
        timestamp: None,
        comission_profit: decimal.Decimal
) -> Game:
    return Game.create(
        user=user_id,
        name=name,
        bid=bid,
        comment=comment,
        status=status,
        timestamp=timestamp,
        comission_profit=comission_profit
    )


def create_user(user_id: int, referral_id: int = None, timestamp: datetime = None):
    user = User.create(
        user_id=user_id,
        referral_id=referral_id,
        timestamp=timestamp or datetime.now()
    )
    return user


def get_user(user_id) -> User | None:
    return User.get_or_none(user_id=user_id)


def get_all_users() -> list[User]:
    return User.select()


def get_user_games(user_id: int) -> list[Game]:
    return Game.select().where(Game.user == user_id)


def get_game(game_id: int) -> Game | None:
    return Game.get_or_none(id=game_id)


def get_games() -> list[Game]:
    return Game.select()

def get_gamses(user_id) -> list[Game]:
    return Game.select().where(Game.user_id == user_id)



def get_referrals(user_id: int) -> list[User]:
    return User.select().where(User.referral_id == user_id)

# utils_db.py

def get_withdrawals_history(time_period: str):
    now = datetime.now()
    
    # Determine the time delta based on the provided time period
    if time_period.endswith("h"):
        h = int(time_period[:-1])
        ago = now - timedelta(hours=h)
        previous_ago = ago - timedelta(hours=h)
    elif time_period.endswith("d"):
        d = int(time_period[:-1])
        ago = now - timedelta(days=d)
        previous_ago = ago - timedelta(days=d)
    else:
        raise ValueError("Unsupported time period format. Use 'h' for hours or 'd' for days.")

    # Выводы за последние time_period часов или дней
    recent_withdrawals = Withdrawal.select().where((Withdrawal.timestamp.is_null(False)) & (Withdrawal.timestamp >= ago))

    # Выводы за аналогичный период ранее
    previous_withdrawals = Withdrawal.select().where((Withdrawal.timestamp.is_null(False)) & (Withdrawal.timestamp >= previous_ago) & (Withdrawal.timestamp < ago))

    # Общая сумма выводов
    total_withdrawn = recent_withdrawals.select(fn.SUM(Withdrawal.amount).alias('sum')).scalar() or 0

    # Сумма выводов за аналогичный период ранее
    previous_withdrawn = previous_withdrawals.select(fn.SUM(Withdrawal.amount).alias('previous_sum')).scalar() or 0

    return {
        "total_withdrawn": float(f"{total_withdrawn:g}"),
        "previous_withdrawn": float(f"{previous_withdrawn:g}")
    }

def get_game_statistics(time_period: str):
    now = datetime.now()
    
    # Determine the time delta based on the provided time period
    if time_period.endswith("h"):
        h = int(time_period[:-1])
        ago = now - timedelta(hours=h)
        previous_ago = ago - timedelta(hours=h)
    elif time_period.endswith("d"):
        d = int(time_period[:-1])
        ago = now - timedelta(days=d)
        previous_ago = ago - timedelta(days=d)
    else:
        raise ValueError("Unsupported time period format. Use 'h' for hours or 'd' for days.")

    # Игры за последние time_period часов или дней, игнорируя записи с null timestamp
    recent_games = Game.select().where((Game.timestamp.is_null(False)) & (Game.timestamp >= ago))

    # Игры за аналогичный период ранее, игнорируя записи с null timestamp
    previous_games = Game.select().where((Game.timestamp.is_null(False)) & (Game.timestamp >= previous_ago) & (Game.timestamp < ago))

    # Количество игр
    total_games = recent_games.count()

    # Количество выигрышей (status = 1) и проигрышей (status = 0)
    wins = recent_games.where(Game.status == 1).count()
    losses = recent_games.where(Game.status == 0).count()
    draws = recent_games.where(Game.status == 2).count()
    commission_profit = recent_games.where(Game.status == 2).select(fn.SUM(Game.comission_profit).alias('commission_profit')).scalar() or decimal.Decimal('0.00')
    
    # Общая сумма ставок
    total_bid = recent_games.select(fn.SUM(Game.bid).alias('sum')).scalar() or 0

    # Прибыль: сумма проигрышей пользователей
    total_profit = recent_games.where(Game.status == 0).select(fn.SUM(Game.bid).alias('profit')).scalar() or 0
    
    # Затраты: сумма выигрышей пользователей
    total_cost = recent_games.where(Game.status == 1).select(fn.SUM(Game.bid).alias('cost')).scalar() or 0

    # Чистый доход: прибыль минус затраты
    net_income = total_profit - total_cost

    # Прибыль за аналогичный период ранее
    previous_profit = previous_games.where(Game.status == 0).select(fn.SUM(Game.bid).alias('previous_profit')).scalar() or 0

    # Рассчитываем изменение прибыльности относительно предыдущего периода
    if previous_profit:
        profitability_change = (total_profit - previous_profit) / previous_profit * 100
    else:
        profitability_change = float('inf') if total_profit else 0

    # Вычисление комиссии CryptoBot
    commission = total_bid * 0.027  # Комиссия 2.7%

    # История выводов
    withdrawals_history = get_withdrawals_history(time_period)
    total_withdrawn = withdrawals_history["total_withdrawn"]

    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "draws": draws, 
        "total_bid": float(f"{total_bid:g}"),
        "total_profit": float(f"{total_profit:g}"),
        "total_cost": float(f"{total_cost:g}"),
        "net_income": float(f"{net_income:g}"),
        "profitability_change": profitability_change,
        "commission": float(f"{commission:g}"),
        "commission_profit": float(f"{commission_profit:.2f}"),
        "total_withdrawn": total_withdrawn,
    }


def get_all_withdrawals():
    return Withdrawal.select(fn.SUM(Withdrawal.amount)).scalar() or 0

def get_total_commission_profit() -> decimal.Decimal:
    total_commission_profit = Game.select(fn.SUM(Game.comission_profit)).scalar()
    return total_commission_profit or decimal.Decimal('0.00')



Game.create_table()
User.create_table()
Withdrawal.create_table()
Queue.create_table()