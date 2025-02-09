import httpx

from core import RestClient


class User(RestClient):
    prefix: str = "/api/v1"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)

    async def user_info(self, **kwargs) -> httpx.Response:
        return await self.get(f"{self.prefix}/user", **kwargs)

    async def user_variable(self, variable_name, **kwargs) -> httpx.Response:
        method = kwargs.pop("method")
        path = f"{self.prefix}/user/actions/variables/{variable_name}"

        if method == "post":
            return await self.post(path, **kwargs)
        elif method == "DELETE":
            return await self.delete(path, **kwargs)
        elif method == "PUT":
            return await self.put(path, **kwargs)
        else:
            return await self.get(path, **kwargs)
