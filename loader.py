from aiocryptopay import AioCryptoPay
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

import config
from cryptopay import CryptoBotPay


cryptopay = CryptoBotPay(AioCryptoPay(config.CRYPTO_PAY_TOKEN))
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
