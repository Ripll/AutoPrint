#8b35930e-d3b0-4a7b-aa34-fa235b7b9959
import aiohttp


class YandexGeocoder:
    def __init__(self, key: str):
        self.key = key

    async def get_geo_by_addr(self, address):
        async with aiohttp.ClientSession() as client:
            params = {
                "apikey": self.key,
                "geocode": address,
                "format": "json"
            }
            async with client.get("https://geocode-maps.yandex.ru/1.x",
                                   params=params) as resp:
                result = await resp.json()
                return result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
