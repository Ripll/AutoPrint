import aiohttp


class IMGBB:
    def __init__(self, key: str):
        self.key = key

    async def upload(self, img=None):
        async with aiohttp.ClientSession() as client:
            params = {
                "key": self.key
            }
            form = {
                "image": img
            }
            async with client.post("https://api.imgbb.com/1/upload",
                                   params=params,
                                   data=form) as resp:
                return (await resp.json())['data']['url']
