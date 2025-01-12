from core.rest_client import RestClient


class User(RestClient):
    def __init__(self, base_url):
        super().__init__(f"{base_url}/api/v1")

    def user_info(self, **kwargs):
        return self.get('/user', **kwargs)

    # def list_all_users(self, **kwargs):
    #     return self.get("/users", **kwargs)
    #
    # def list_one_user(self, username, **kwargs):
    #     return self.get("/users/{}".format(username), **kwargs)
    #
    # def register(self, **kwargs):
    #     return self.post("/register", **kwargs)
    #
    # def login(self, **kwargs):
    #     return self.post("/login", **kwargs)
    #
    # def update(self, user_id, **kwargs):
    #     return self.put("/update/user/{}".format(user_id), **kwargs)
    #
    # def delete(self, name, **kwargs):
    #     return self.post("/delete/user/{}".format(name), **kwargs)
