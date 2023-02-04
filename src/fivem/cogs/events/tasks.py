import asyncio
import disnake
import typing as t
from disnake.ext import plugins
from disnake.ext import tasks
from fivem.helpers.fivem_ip import fivem_data
from fivem.db import cache, db
from aiocache import caches


plugin = plugins.Plugin()


@plugin.register_loop(wait_until_ready=True)
@tasks.loop(seconds=1800)
async def daily_update():
    _cache = caches.get("default")
    data = await _cache.get("all_servers")

    if not data:
        data = await cache.all_servers(plugin.bot)

    for d in data:
        code = d["cfx_code"]
        link = f"cfx.re/join/{code}"
        server_info = await fivem_data(link=link)
        cached_data = await _cache.get(f"server_data:{code}") or await cache.server_data(plugin.bot, code)

        if int(cached_data[0]["daily_high"]) < int(server_info["Data"]["selfReportedClients"]):
            await db.update_daily_high(plugin.bot, code, server_info["Data"]["selfReportedClients"])
            await _cache.delete(f"server_data:{code}")
            await cache.server_data(plugin.bot, code)

        if int(cached_data[0]["daily_low"]) > int(server_info["Data"]["selfReportedClients"]):
            await db.update_daily_low(plugin.bot, code, server_info["Data"]["selfReportedClients"])
            await _cache.delete(f"server_data:{code}")
            await cache.server_data(plugin.bot, code)


@plugin.register_loop(wait_until_ready=True)
@tasks.loop(hours=24)
async def daily_avg_update():
    _cache = caches.get("default")
    data = await _cache.get("all_servers")

    if not data:
        data = await cache.all_servers(plugin.bot)

    for d in data:
        code = d["cfx_code"]
        link = f"cfx.re/join/{code}"
        server_info = await fivem_data(link=link)
        cached_data = await _cache.get(f"server_data:{code}")
        if not cached_data:
            cached_data = await cache.server_data(plugin.bot, code)

        avg = int(cached_data[0]["daily_high"]) + \
            int(cached_data[0]["daily_low"])
        avg = avg/2
        await db.update_daily_avg(plugin.bot, code, avg)
        _cache = caches.get('default')
        await _cache.delete(f"server_data{code}")
        await cache.server_data(plugin.bot, code)

setup, teardown = plugin.create_extension_handlers()
