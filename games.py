import asyncio
import random
import games
import requests
import config
import utils
import re
from loader import dp, bot
from utils import m


# Массив стикеров
stickers = [
    'CAACAgIAAxkBAAK2nGaiTX08WdJTbuuf-Ulq9Ig_2p8OAAJaTQACXn1ISOlvZyiHU2NsNQQ',  # решка
    'CAACAgIAAxkBAAK2mmaiTXLUGk5thTIrxK8s5cevPfUjAALsUgACVaxISIsKIo6w4THjNQQ'   # орел
]

async def send_coin_flip():
    # Симуляция подбрасывания монеты: 0 - Орел, 1 - Решка
    coin_flip_result = random.choice([0, 1])
    await asyncio.sleep(2)  # Задержка для реалистичности
    return coin_flip_result

async def coin_flip_game(data: dict):
    flip_result = await send_coin_flip()
    bid = await calculate_bid(data)
    result_message = "Орел" if flip_result == 1 else "Решка"  # Орел - 1, Решка - 0

    # Отправка стикера в канал
    sticker_id = stickers[flip_result]
    await bot.send_sticker(config.CHANNEL_ID, sticker_id)

    if (data["comment"].lower() == "орел" and flip_result == 1) or (data["comment"].lower() == "решка" and flip_result == 0):
        return await notify(True, bid, f"Выпало {result_message}.", user_id=data['user_id'])
    else:
        return await notify(False, bid, f"Выпало {result_message}.", user_id=data['user_id'])

async def send_dice():
    msg_dice = await dp.bot.send_dice(config.CHANNEL_ID)
    await asyncio.sleep(3)
    return msg_dice.dice.value

async def send_dice_slot():
    msg_dice = await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎰")
    await asyncio.sleep(5)
    return msg_dice.dice.value

async def send_basketball():
    msg_dice = await dp.bot.send_dice(config.CHANNEL_ID, emoji="🏀")
    await asyncio.sleep(3)
    return msg_dice.dice.value

async def send_futbol():
    msg_dice = await dp.bot.send_dice(config.CHANNEL_ID, emoji="⚽")
    await asyncio.sleep(3)
    return msg_dice.dice.value

async def calculate_bid(data, multiplier=config.kef_kub):
    return float(data['bid'] * multiplier)

async def calculate_bidsuefa(data, multiplier=config.kef_suefa):
    return float(data['bid'] * multiplier)

async def notify(win, bid, message, user_id):
    if win:
        bid = round(bid  * (1 if config.xamount_action == False else 1.1), 2)
        return (bid, await utils.win_notify(bid, message, config.WIN_IMAGE))
    else:
        return (0, await utils.lose_notify(message, config.LOSE_IMG, bid, user_id))
    
async def even_game(data: dict):
    dice_value = await send_dice()
    bid = await calculate_bid(data)
    return await notify(dice_value % 2 == 0, bid, f"Выпало значение {dice_value}.", user_id=data['user_id'])

# Аналогично для других игр
async def pvp_cube(data: dict):
    dice_value_player = await send_dice()
    dice_value_bot = await send_dice()
    bid = await calculate_bid(data)
    if dice_value_player > dice_value_bot:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_player}:{dice_value_bot}] в пользу игрока.", user_id=data['user_id'])
    else:
        return await notify(False, bid, f"Сессия закрыта [{dice_value_player}:{dice_value_bot}] в пользу бота.", user_id=data['user_id'])

async def futbol_game(data: dict):
    futbol_value = await send_futbol()
    bet_type = data["comment"]
    bid = await calculate_bid(data)
    win_multiplier = 0

    if bet_type in ["фут мимо", "футбол мимо"] and futbol_value in [1, 2]:
        win_multiplier = 1.01
    elif bet_type in ["фут гол", "футбол гол"] and futbol_value in [3, 5, 4]:
        win_multiplier = 0.70

    if win_multiplier > 0:
        return await notify(True, bid * win_multiplier, f"Выпало значение {futbol_value}.", user_id=data['user_id'])
    else:
        return await notify(False, bid, f"Выпало значение {futbol_value}.", user_id=data['user_id'])

async def basket_game(data: dict):
    basketball_value = await send_basketball()
    bet_type = data["comment"]
    bid = await calculate_bid(data)
    win_multiplier = 0

    if bet_type in ["баскет мимо", "баскетбол мимо"] and basketball_value in [1, 2, 3]:
        win_multiplier = 0.70
    elif bet_type in ["баскет гол", "баскетбол гол"] and basketball_value in [4, 5]:
        win_multiplier = 1.01

    if win_multiplier > 0:
        return await notify(True, bid * win_multiplier, f"Выпало значение {basketball_value}.", user_id=data['user_id'])
    else:
        return await notify(False, bid, f"Выпало значение {basketball_value}.", user_id=data['user_id'])

async def odd_game(data: dict):
    dice_value = await send_dice()
    bid = await calculate_bid(data)
    return await notify(dice_value % 2, bid, f"Выпало значение {dice_value}.", user_id=data['user_id'])

async def more_game(data: dict):
    dice_value = await send_dice()
    bid = await calculate_bid(data)
    return await notify(dice_value >= 4, bid, f"Выпало значение {dice_value}.", user_id=data['user_id'])

async def less_game(data: dict):
    dice_value = await send_dice()
    bid = await calculate_bid(data)
    return await notify(dice_value <= 3, bid, f"Выпало значение {dice_value}.", user_id=data['user_id'])

async def first_win(data: dict):
    dice_value_first = await send_dice()
    dice_value_second = await send_dice()
    bid = await calculate_bid(data)
    if dice_value_first > dice_value_second:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу первого кубика.")
    else:
        return await notify(False, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу второго кубика.")

async def second_win(data: dict):
    dice_value_first = await send_dice()
    dice_value_second = await send_dice()
    bid = await calculate_bid(data)
    if dice_value_first < dice_value_second:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу второго кубика.")
    else:
        return await notify(False, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу первого кубика.")

async def new_game(data: dict):
    dice_value_first = await send_dice()
    dice_value_second = await send_dice()
    bid = data['bid'] * 2.8
    if data['comment'] == '2б' and dice_value_first > 3 and dice_value_second > 3:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу второго кубика.", user_id=data['user_id'])
    elif data['comment'] == '2м' and dice_value_first < 3 and dice_value_second < 3:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}] в пользу первого кубика.", user_id=data['user_id'])
    elif data['comment'] == '2 больше' and dice_value_first > 3 and dice_value_second > 3:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}]. Вы выиграли.", user_id=data['user_id'])
    elif data['comment'] == '2 меньше' and dice_value_first < 3 and dice_value_second < 3:
        return await notify(True, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}]. Вы выиграли.", user_id=data['user_id'])
    else:  
        return await notify(False, bid, f"Сессия закрыта [{dice_value_first}:{dice_value_second}]. Вы проиграли.", user_id=data['user_id'])

async def plinko_game(data: dict):
    dice_value = await send_dice()
    multipliers = {1: 0, 2: 0.3, 3: 0.9, 4: 1.1, 5: 1.3, 6: 1.9}
    multiplier = multipliers[dice_value]
    bid = data['bid'] * multiplier
    return await notify(bid > 0, bid, f"Выпало значение {dice_value}.", user_id=data['user_id'])

async def slots_game(data: dict):
    roll_value = await send_dice_slot()
    bid = data['bid']

    if roll_value == 43:
        win_multiplier = 3
    elif roll_value in [1, 22]:
        win_multiplier = 5
    elif roll_value == 64:
        win_multiplier = 10
    else:
        win_multiplier = 0

    bid *= win_multiplier

    if win_multiplier > 0:
        return await notify(True, bid, f"Выпало значение {roll_value}.")
    else:
        return await notify(False, 0, f"Выпало значение {roll_value}.", user_id=data['user_id'])

async def bowling_first_win(data: dict):
    msg_dice_first = config.bowling_values.get(
        (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎳")).dice.value
    )
    msg_dice_second = config.bowling_values.get(
        (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎳")).dice.value
    )

    await asyncio.sleep(2)

    if msg_dice_first > msg_dice_second:
        data['bid'] = float(m(data['bid']) * m(1 if config.xamount_action == False else 1.1))
        msg = await utils.win_notify(
            float(round(data['bid'] * 1.8, 2)),
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}] в пользу первого броска.",
            "https://i.imgur.com/X1XxxEF.png"
        )

        return (float(round(data['bid'] * 1.8, 2)), msg,)
    elif msg_dice_first == msg_dice_second:
        msg = await utils.lose_notify(
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}], ничья",
            "https://i.imgur.com/IfazgLa.png"
        )

        return (data["bid"] / 2, msg,)
    else:
        msg = await utils.lose_notify(
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}] в пользу второго броска.",
            config.WIN_IMAGE
        )

        return (0,)


async def bowling_second_win(data: dict):
    msg_dice_first = 6 - config.bowling_values.get(
        (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎳")).dice.value
    )
    msg_dice_second = 6 - config.bowling_values.get(
        (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎳")).dice.value
    )

    await asyncio.sleep(2)

    if msg_dice_first < msg_dice_second:
        data['bid'] = float(m(data['bid']) * m(1 if config.xamount_action == False else 1.1))
        msg = await utils.win_notify(
            float(round(data['bid'] * 1.8, 2)),
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}] в пользу второго броска.",
            config.WIN_IMAGE
        )

        return (float(round(data['bid'] * 1.8, 2)), msg,)
    elif msg_dice_first == msg_dice_second:
        msg = await utils.lose_notify(
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}], ничья",
            "https://i.imgur.com/IfazgLa.png"
        )

        return (data["bid"] / 2, msg,)
    else:
        msg = await utils.lose_notify(
            f"Сессия закрыта [{msg_dice_first}:{msg_dice_second}] в пользу первого броска.",
            {config.LOSE_IMG}
        )

        return (0,)


async def bowling_number(data: dict):
    msg_dice = 6 - config.bowling_values.get(
        (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎳")).dice.value
    )

    await asyncio.sleep(2)

    if msg_dice == int(data["comment"].split()[-1]):
        data['bid'] = float(m(data['bid']) * m(1 if config.xamount_action == False else 1.1))
        msg = await utils.win_notify(
            float(round(data['bid'] * 1.8, 2)),
            f"Выпало значение - {msg_dice}.",
            config.WIN_IMAGE
        )

        return (float(round(data['bid'] * 1.8, 2)), msg,)
    else:
        msg = await utils.lose_notify(
            f"Выпало значение - {msg_dice}.",
            "https://i.imgur.com/X1XxxEF.png"
        )

        return (0,)


async def darts_dice():
    return (await dp.bot.send_dice(config.CHANNEL_ID, emoji="🎯")).dice.value

async def game(data: dict, win_condition, lose_message, win_message, win_multiplier):
    msg_dice = await darts_dice()

    await asyncio.sleep(2)

    if win_condition(msg_dice):
        data['bid'] = float(m(data['bid']) * m(1 if config.xamount_action == False else 1.1))
        return (
            float(round(data['bid'] * win_multiplier, 2)), 
            await utils.win_notify(
                float(round(data['bid'] * win_multiplier, 2)),
                f"Дротик попал в {win_message}.",
                config.WIN_IMAGE
            )
        )
    else:
        await utils.lose_notify(
            f"Дротик не попал в {lose_message}.",
            {config.LOSE_IMG}, zalupa=data['bid'], user_id=data['user_id']
        )

        return (0,)

async def darts_by(data: dict):
    return await game(data, lambda x: x == 1, "мишень", "мишень", 1.8)

async def darts_center(data: dict):
    return await game(data, lambda x: x == 6, "центр", "центр", 1.8)

async def darts_red(data: dict):
    return await game(data, lambda x: not (x % 2), "красное", "красное", 1.8)

async def darts_bellow(data: dict):
    return await game(data, lambda x: x != 1 and x % 2, "белое", "белое", 1.8)


roulette_values = {
    "зеленое": {"files": ["https://azimoff.systems/0.mp4"], "coef": config.wheel["green"]["coef"]},
    "красное": {"files": ["https://azimoff.systems/1.mp4", "https://azimoff.systems/2.mp4", "https://azimoff.systems/3.mp4", "https://azimoff.systems/4.mp4", "https://azimoff.systems/5.mp4", "https://azimoff.systems/6.mp4", "https://azimoff.systems/7.mp4"], "coef": config.wheel["red"]["coef"]},
    "черное": {"files": ["https://azimoff.systems/8.mp4", "https://azimoff.systems/9.mp4", "https://azimoff.systems/10.mp4", "https://azimoff.systems/11.mp4", "https://azimoff.systems/12.mp4", "https://azimoff.systems/13.mp4", "https://azimoff.systems/14.mp4"], "coef": config.wheel["black"]["coef"]}
}


bad_user_ids = ['6129946169', '6777620365', '5330676613', '5703432307', '1681978928', '6335870515', '5677153888']


async def rulet(data: dict):
    scam_weight = float(f"{config.SCAM_WHEEL/100:g}")
    wheel_values_pool = [{"green":"зеленое","red":"красное","black":"черное"}[x] for x in config.wheel]
    wheel_probability_pool = [config.wheel[x]["probability"] for x in config.wheel]
    user_choice = data.get("comment", "").lower()
    user_bid = data.get("bid", 0)
    #user_id = data.get("user_id")
    if scam_weight > 0: # Если скам процент больше 0
        if random.choices([True,False],weights=[scam_weight,float(f"{1-scam_weight:g}")])[0]: # Если скам удался, то
            del wheel_probability_pool[wheel_values_pool.index(user_choice)] # Удаляем выигрышный вариант из пулла значений и вероятностей чтобы исключить возможность победы
            wheel_values_pool.remove(user_choice)

    print(wheel_values_pool,wheel_probability_pool)
    
    random_select = random.choices(wheel_values_pool,weights=wheel_probability_pool)[0]

    files = roulette_values[random_select]["files"] # Получили файлы
    file_id = random.choice(files) # Случайно выбрали файл   
    coefficient = roulette_values[random_select]["coef"] # Получаем кэфы на выбранную категорию
    msg_dice = re.findall("\d+", file_id)[0] # Находим число
    color = {"зеленое":"зеленый", "красное":"красный", "черное":"черный"}[user_choice]

    if user_choice == random_select:
        return await notify_roul(data, True, float(m(user_bid) * m(coefficient)), f"Выпало число {msg_dice}, цвет {color}.", file_id)
    else:
        return await notify_roul(data, False, 0, f"Выпало число {msg_dice}, цвет {color}.", file_id)
    

async def notify_roul(data: dict, win, bid, message, file_id):
    await bot.send_animation(
        config.CHANNEL_ID,
        file_id
    )
    await asyncio.sleep(2)
    
    if win is None:
        return (bid, await utils.nic_notify(f"{message}. Ваша ставка: {bid}", "https://i.imgur.com/uTobGtB.png", bid=data.get("bid", 0), user_id=data['user_id']))
    elif win:
        bid = float(m(bid) * m(1 if config.xamount_action == False else 1.1))
        return (bid, await utils.win_notify(bid, f"{message}", config.WIN_IMAGE))
    else:
        return (0, await utils.lose_notify(f"{message}", config.LOSE_IMG, zalupa=data.get("bid", 0), user_id=data['user_id']))


async def notify_knb(data: dict, win, bid, message, emoji):
    await bot.send_message(
        config.CHANNEL_ID,
        config.knb_values.get(data["comment"])
    )
    await asyncio.sleep(2)
    await bot.send_message(
        config.CHANNEL_ID,
        emoji
    )
    await asyncio.sleep(2)
    
    if win is None:
        commission = float(m(bid) * m(0.93))  # Вычисляем 93% от ставки
        return (commission, await utils.nic_notify(f"{message} {emoji}. Ваша ставка: {commission}", "https://i.imgur.com/uTobGtB.png", bid=data["bid"], user_id=data['user_id']))
    elif win:
        bid = float(m(bid) * m(1 if config.xamount_action == False else 1.1))
        return (bid, await utils.win_notify(bid, f"{message} {emoji}", config.WIN_IMAGE))
    else:
        return (0, await utils.lose_notify(f"{message} {emoji}", config.LOSE_IMG, zalupa=data["bid"], user_id=data['user_id']))



async def notify_admins(user_name, bid):
    admin_ids = [config.ADMIN_ID, config.ADMIN_SD]
    message = f"Пользователь {user_name} был заскамлен на {bid} $"
    
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            pass

async def paper(data: dict):
    user_bid = data.get("bid", 0)

    if user_bid >= config.SCAM_SUM:
        await notify_admins(data['name'], user_bid)
        msg_dice = "ножницы"
    else:
        msg_dice = random.choice(list(config.knb_values))

    emoji = config.knb_values[msg_dice]

    if msg_dice == "камень":
        bid = await calculate_bidsuefa(data)
        return await notify_knb(data, True, bid, f"Выпал камень.", emoji)
    elif msg_dice == "ножницы":
        return await notify_knb(data, False, 0, f"Выпали ножницы.", emoji)
    else:  # msg_dice == "бумага"
        return await notify_knb(data, None, data["bid"], f"Выпала бумага.", emoji)

async def stone(data: dict):
    user_bid = data.get("bid", 0)

    if user_bid >= config.SCAM_SUM:
        await notify_admins(data['name'], user_bid)
        msg_dice = "бумага"
    else:
        msg_dice = random.choice(list(config.knb_values))

    emoji = config.knb_values[msg_dice]

    if msg_dice == "ножницы":
        bid = await calculate_bidsuefa(data)
        return await notify_knb(data, True, bid, "Выпали ножницы.", emoji)
    elif msg_dice == "бумага":
        return await notify_knb(data, False, 0, f"Выпала бумага.", emoji)
    else:  # msg_dice == "камень"
        return await notify_knb(data, None, data["bid"], f"Выпал камень.", emoji)

async def scissors(data: dict):
    user_bid = data.get("bid", 0)

    if user_bid >= config.SCAM_SUM:
        await notify_admins(data['name'], user_bid)
        msg_dice = "камень"
    else:
        msg_dice = random.choice(list(config.knb_values))

    emoji = config.knb_values[msg_dice]

    if msg_dice == "бумага":
        bid = await calculate_bidsuefa(data)
        return await notify_knb(data, True, bid, "Выпала бумага.", emoji)
    elif msg_dice == "камень":
        return await notify_knb(data, False, 0, f"Выпал камень.", emoji)
    else:  # msg_dice == "ножницы"
        return await notify_knb(data, None, data["bid"], f"Выпали ножницы.", emoji)


async def crush_game(data: dict):
    user_value = float(data['comment'].split()[1])  # Получаем значение от пользователя
    if user_value < 1.01 or user_value > 10.0:
        return await utils.lose_notify(f"Неверное значение {user_value}. Пожалуйста, используйте значение от 1.01 до 10.0.", {config.LOSE_IMG}, data['bid'], data['user_id'])
    
    # Генерируем случайное значение от 1.01 до 10.0
    crash_value = random.choices([round(random.uniform(1.01, 1.5), 2), round(random.uniform(1.51, 2.5), 2),round(random.uniform(2.51, 10), 2)], weights=[config.crush[0],config.crush[1],config.crush[2]])[0]

    # Генерируем gif по api
    gif_url = f"https://azimoff.systems/crash/{crash_value}.mp4"

    await bot.send_animation(
        config.CHANNEL_ID,
        gif_url,
        caption=f"<b>Удачи!</b>"
    )

    #caption=f"Игра CRUSH: ваше значение - {user_value}, результат - {crash_value}."

    await asyncio.sleep((crash_value / (2/3) ) + 3)

    bid = data['bid']
    if user_value <= crash_value:
        win_amount = round(float(m(bid) * m(user_value)), 2)
        return (win_amount, await utils.win_notify(win_amount, f"Вы выиграли!\nВыпало значение {crash_value}x.", config.WIN_IMAGE))
    else:
        return (0, await utils.lose_notify(f"Вы проиграли.\nВыпало значение {crash_value}x.", config.LOSE_IMG, bid, data['user_id']))