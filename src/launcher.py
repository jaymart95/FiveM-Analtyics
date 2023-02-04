import asyncio
from fivem.bot import FiveMBot
import logging
import config

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


async def main():
    bot = FiveMBot()
    try:
        bot._load_extensions("fivem.cogs")
        await bot.create_db_pool()
        await bot.start(config.TOKEN)

    except KeyboardInterrupt:
        bot.close()


asyncio.run(main())
