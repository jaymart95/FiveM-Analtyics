import disnake
from disnake.ext import plugins
from fivem.cogs.etc.views import Menu
from fivem.db import cache, db
from fivem.helpers.fivem_ip import fivem_data
import re
from aiocache import caches

plugin = plugins.Plugin()
_cache = caches.get("default")


@plugin.listener()
async def on_button_click(inter: disnake.MessageInteraction):
    await inter.response.defer()
    if "yes" in inter.component.custom_id:
        code = inter.component.custom_id.split(":")[1]
        link = f"cfx.re/join/{code}"
        data = await fivem_data(link)
        server_name = data["Data"]["hostname"].split("|")[0]
        server_name = re.sub(r"[^a-zA-Z]+", "", server_name)
        await db.newServer(plugin.bot, code, server_name, data["Data"]["ownerAvatar"], data["Data"]["selfReportedClients"], data["Data"]["selfReportedClients"])
        await _cache.delete("all_servers")
        embed = inter.message.embeds[0]
        embed.set_footer(text="Server is now being tracked.")
        await inter.send(embed=embed)

    if "stats" in inter.component.custom_id:
        code = inter.component.custom_id.split(":")[1]
        data = await cache.server_data(plugin.bot, code)
        if not data:
            embed = inter.message.embeds[0]
            embed.set_footer(
                text="Server is not being tracked. Click the button below to add it to the database.")
            components = [
                disnake.ui.Button(label="Add Server", custom_id="yes:{}".format(
                    code), style=disnake.ButtonStyle.green),
            ]
            return await inter.message.edit(embed=embed, components=components)

        embed = disnake.Embed(
            title="{} Player Statistics".format(data[0]["server_name"]))
        embed.set_thumbnail(url=data[0]["img"])
        embed.add_field(name="Daily Average",
                        value="`{}`".format(data[0]["daily_avg"]), inline=False)
        embed.add_field(name="Weekly Average",
                        value="`{}`".format(data[0]["weekly_avg"]), inline=False)
        embed.add_field(name="Monthly Average",
                        value="`{}`".format(data[0]["monthly_avg"]), inline=False)
        embed.add_field(name="Daily Player\nHigh",
                        value="`{}`".format(data[0]["daily_high"]))
        embed.add_field(name="Daily Player\nLow",
                        value="`{}`".format(data[0]["daily_low"]))
        await inter.message.edit(embed=embed)

    if "resources" in inter.component.custom_id:
        code = inter.component.custom_id.split(":")[-1]
        data = await fivem_data("cfx.re/join/{}".format(code))
        server_name = data["Data"]["hostname"].split("|")[0]
        server_name = re.sub(r"[^a-zA-Z]+", "", server_name)
        resources = data['Data']['resources']
        chunks = [resources[x:x+10] for x in range(0, len(resources), 10)]
        embeds = []
        for chunk in chunks:
            embed = disnake.Embed(title=f"{server_name} Resources")
            for _resource in chunk:
                embed.add_field(name=_resource, value="`{}`".format(
                    _resource), inline=False)
            embeds.append(embed)
        await inter.message.edit(embed=embeds[0], view=Menu(embeds))

    if "players" in inter.component.custom_id:
        await inter.message.edit(embed=disnake.Embed(title="Loading players", description="<a:2923printsdark:1070819971850043504>"))
        code = inter.component.custom_id.split(":")[-1]
        data = await fivem_data("cfx.re/join/{}".format(code))
        server_name = data["Data"]["hostname"].split("|")[0]
        server_name = re.sub(r"[^a-zA-Z]+", "", server_name)
        players = data['Data']['players']
        chunks = [players[x:x+10] for x in range(0, len(players), 10)]
        embeds = []
        for chunk in chunks:
            embed = disnake.Embed(title=f"{server_name} Players")
            for _player in chunk:
                for d in _player['identifiers']:
                    if "discord" in d:
                        try:
                            user_id = d.split(":")[2]
                            user = await plugin.bot.get_user(int(user_id))
                        except:
                            user_id = d.split(":")[1]
                            user = await plugin.bot.fetch_user(int(user_id))
                embed.add_field(
                    name=_player['name'], value=f"{user.mention}", inline=False)
            embeds.append(embed)
        await inter.message.edit(embed=embeds[0], view=Menu(embeds))

setup, teardown = plugin.create_extension_handlers()
