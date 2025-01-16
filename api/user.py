import httpx
import requests

from core import RestClient


class User(RestClient):

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)

    async def user_info(self, **kwargs) -> requests.Response:
        return await self.get("/api/v1/user", **kwargs)
