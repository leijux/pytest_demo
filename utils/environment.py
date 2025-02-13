import os
from typing import Optional


class Environment:
    def __init__(self):
        self._base_url: Optional[str] = os.getenv("BASE_URL")

        for key, value in self.__dict__.items():
            if value is None:
                raise ValueError(f"Environment variable {key} is empty")

    @property
    def BASE_URL(self) -> str:
        return self._base_url


env = Environment()
