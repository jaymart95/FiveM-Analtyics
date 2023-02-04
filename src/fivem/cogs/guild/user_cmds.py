import disnake
import typing as t
from disnake.ext import plugins
from fivem.helpers.fivem_ip import fivem_data
import re
from thefuzz import process
from aiocache import caches
from fivem.db import cache, db


plugin = plugins.Plugin()


def embed_builder(title, owner, owner_img, thumbnail) -> None:
    embed = disnake.Embed(title=title)
    embed.set_author(name=owner, icon_url=owner_img)
    embed.set_thumbnail(thumbnail)
    return embed


@plugin.slash_command(name="lookup")
async def server_lookup(inter: disnake.ApplicationCommandInteraction,
                        cfx_link: t.Optional[str]):
    await inter.response.defer(with_message=True)

    if cfx_link:
        if "cfx.re/join/" in cfx_link:
            cfx_link.replace("cfx.re/join/", "")

        data = await fivem_data(link=cfx_link)
        max_client = data["Data"]["svMaxclients"]
        current_players = data["Data"]["selfReportedClients"]
        server_name = data["Data"]["hostname"]
        server_name.replace('^', "")
        if len(server_name) > 20:
            server_name = server_name[0:20] + "...."

        if "Owner" in data["Data"]["vars"]:
            owner = data["Data"]["vars"]["Owner"]

        if "ownerName" in data["Data"]:
            owner = data["Data"]["ownerName"]

        if "Uptime" in data["Data"]["vars"]:
            uptime = data["Data"]["vars"]["Uptime"]

        if "Uptime" not in data["Data"]["vars"]:
            uptime = "N/A"

        embed = disnake.Embed(title=f"".join(server_name))
        embed.set_author(name=owner,
                         icon_url=data["Data"]["ownerAvatar"])
        # embed.set_image(url=data["Data"]["vars"]["banner_detail#original_url"])
        embed.set_thumbnail(url=data["Data"]["ownerAvatar"])
        embed.add_field(
            name='Players', value=f"`{current_players}`")
        embed.add_field(name="Resources", value="`{}`".format(
            len(data["Data"]["resources"])))
        embed.add_field(name="Uptime", value=f"`{uptime}`")
        embed.add_field(name="Upvotes", value="`{}`".format(
            data["Data"]["upvotePower"]))

        code = cfx_link.split("/")[-1]
        buttons = [
            disnake.ui.Button(
                label="Statistics",
                style=disnake.ButtonStyle.green,
                custom_id=f"stats:{code}"
            ),
            disnake.ui.Button(
                label="Resources",
                style=disnake.ButtonStyle.red,
                custom_id=f"resources:{code}"
            ),
            disnake.ui.Button(
                label="Player List",
                style=disnake.ButtonStyle.blurple,
                custom_id=f"players:{code}"
            )
        ]
        await inter.send(embed=embed, components=buttons)


@plugin.slash_command(name="add_server")
async def add_server(inter: disnake.ApplicationCommandInteraction, cfx_link: str):
    """Add a server to be tracked daily."""
    await inter.response.defer(with_message=True, ephemeral=True)
    code = cfx_link.split("/")[2]
    data = await fivem_data(cfx_link)
    server_name = data["Data"]["hostname"].split("|")[0]
    server_name = re.sub(r"[^a-zA-Z]+", "", server_name)
    embed = embed_builder(title=f"".join(server_name),
                          owner=data["Data"]["vars"]["Owner"] if not None else data["Data"]["ownerName"],
                          owner_img=data["Data"]["ownerAvatar"],
                          thumbnail=data["Data"]["ownerAvatar"])
    embed.set_footer(
        text="If this is your server please click\nyes below, otherwise click cancel.")

    components = [
        disnake.ui.Button(
            label='Yes',
            style=disnake.ButtonStyle.green,
            custom_id=f"yes:{code}")
    ]
    await inter.send(embed=embed, components=components)


@plugin.slash_command(name="stats")
async def server_stats(self, inter: disnake.ApplicationCommandInteraction, server: str):
    """Show statistics for servers currently being tracked."""
    await inter.response.defer(with_message=True)
    data = await db.get_server_by_name(plugin.bot, server)
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
    await inter.send(embed=embed)


@server_stats.autocomplete("server")
async def stats_autocomplete(inter: disnake.ApplicationCommandInteraction, server: str):
    _cache = caches.get("default")
    data = await _cache.get("all_servers")
    if not data:
        data = await cache.all_servers(plugin.bot)
    servers = []
    for d in data:
        servers.append(d["server_name"])

    values: list[str] = process.extract(server, servers, limit=25)
    return [i[0] for i in values]


setup, teardown = plugin.create_extension_handlers()
