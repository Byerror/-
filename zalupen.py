import asyncio
from aiocryptopay import AioCryptoPay, Networks

crypto = AioCryptoPay(token='143097:AAQm8nxMTynkERJP8VFXQEYfFpU4tmglEWR', network=Networks.MAIN_NET)

async def get_last_transfers(asset='USDT'):
    transfers = await crypto.get_transfers(asset=asset, count=50000)
    for transfer in transfers:
        print(transfer)

# Создаем событийный цикл
loop = asyncio.get_event_loop()
# Запускаем функцию get_last_transfers в событийном цикле
loop.run_until_complete(get_last_transfers())