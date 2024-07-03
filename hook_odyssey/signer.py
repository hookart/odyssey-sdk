from typing import Tuple

from .config import Environment
from .types import PlaceOrderInput


class OdysseySigner:
    def __init__(self, env: Environment, private_key: str):
        self._env = env
        self._private_key = private_key.removeprefix("0x")

    def sign_order(self, order: PlaceOrderInput) -> Tuple[str, str]:
        return "", ""
