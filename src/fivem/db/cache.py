import logging

import disnake
from aiocache import cached, caches
from aiocache.serializers import PickleSerializer, JsonSerializer, StringSerializer, NullSerializer
from fivem.db.db import get_server, get_all_servers
from disnake.ext import plugins


@cached(ttl=21600, key_builder=lambda f, *args: f"{f.__name__}:{args[1]}", serializer=NullSerializer(),)
async def server_data(bot, cfx_code: str):
    datas = await get_server(bot, cfx_code)
    if not datas:
        return False
    return (datas)


@cached(ttl=21600, key_builder=lambda f, *args: f"{f.__name__}", serializer=NullSerializer(),)
async def all_servers(bot):
    datas = await get_all_servers(bot)
    if not datas:
        return False
    return (datas)
