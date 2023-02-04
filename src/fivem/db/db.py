import datetime
from disnake.ext.commands import Bot


async def newServer(bot: Bot, cfx: str, server_name: str, image: str, high: int, low: int):
    async with bot.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO servers (cfx_code, server_name, daily_high, daily_low, daily_avg) VALUES ($1, $2, $3, $4, $5)",
            cfx,
            server_name,
            high,
            low,
            high

        )


async def update_daily_high(bot: Bot, cfx: str, count: int, ip: str = None):
    async with bot.db.acquire() as conn:
        await conn.execute(
            "UPDATE servers SET daily_high = $1 WHERE cfx_code = $2",
            count,
            cfx
        )


async def update_daily_low(bot: Bot, cfx: str, count: int, ip: str = None):
    async with bot.db.acquire() as conn:
        await conn.execute(
            "UPDATE servers SET daily_low = $1 WHERE cfx_code = $2",
            count,
            cfx

        )


async def update_daily_avg(bot: Bot, cfx: str, count: int):
    async with bot.db.acquire() as conn:
        await conn.execute(
            "UPDATE servers SET daily_avg = $1 WHERE cfx_code = $2",
            count,
            cfx
        )


async def get_all_servers(bot: Bot):
    async with bot.db.acquire() as conn:
        data = await conn.fetch(
            "SELECT * FROM servers"
        )
        data = [dict(code) for code in data]
        return data


async def get_server(bot: Bot, cfx: str):
    async with bot.db.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM servers WHERE cfx_code = $1",
            cfx
        )


async def get_server_by_name(bot: Bot, name: str):
    async with bot.db.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM servers WHERE server_name = $1",
            name
        )
