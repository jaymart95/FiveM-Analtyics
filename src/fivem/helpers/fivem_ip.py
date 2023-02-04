import aiohttp

HEADERS = {
    'User-Agent': "Magic Browser"
}


async def fivem_data(link: str = None, ip: int = None, port: int = None):
    if link:
        code = link.split("/")[2]
        url = f"https://servers-frontend.fivem.net/api/servers/single/{code}"

    else:
        url = f"http://{ip}:{port}/players.json"

    async with aiohttp.request("GET", url, headers=HEADERS) as r:
        if r.status == 200:
            json_data = await r.json()

    return json_data
