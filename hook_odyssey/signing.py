from typing import Tuple

from eth_account import Account
from eth_account.messages import (
    SignableMessage,
    _hash_eip191_message,
    encode_typed_data,
)
from web3 import Web3

from .config import Environment
from .types import OrderDirection, PlaceOrderInput

_types = {
    "Order": [
        {"name": "market", "type": "bytes32"},
        {"name": "instrumentType", "type": "uint8"},
        {"name": "instrumentId", "type": "bytes32"},
        {"name": "direction", "type": "uint8"},
        {"name": "maker", "type": "uint256"},
        {"name": "taker", "type": "uint256"},
        {"name": "amount", "type": "uint256"},
        {"name": "limitPrice", "type": "uint256"},
        {"name": "expiration", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "counter", "type": "uint256"},
        {"name": "postOnly", "type": "bool"},
        {"name": "reduceOnly", "type": "bool"},
        {"name": "allOrNothing", "type": "bool"},
    ],
}


class OdysseySigner:
    def __init__(self, env: Environment, private_key: str):
        self._env = env
        self._private_key = private_key.removeprefix("0x")
        self._w3 = Web3()
        self._account = Account.from_key(self._private_key)
        self._domain_data = {
            "name": self._env.value.domain.name,
            "version": self._env.value.domain.version,
            "chainId": self._env.value.domain.chain_id,
            "verifyingContract": self._env.value.domain.verifyingContract,
        }

    def sign_order(self, order: PlaceOrderInput) -> Tuple[str, str]:
        message_data = {
            "market": order.marketHash,
            "instrumentType": 2,  # Change if not Perpetual
            "instrumentId": order.instrumentHash,
            "direction": 0 if order.direction == OrderDirection.BUY else 1,
            "maker": order.subaccount,
            "taker": 0,
            "amount": order.size,
            "limitPrice": order.limitPrice if order.limitPrice is not None else 0,
            "expiration": order.expiration if order.expiration is not None else 0,
            "nonce": order.nonce,
            "counter": 0,
            "postOnly": order.postOnly if order.postOnly is not None else False,
            "reduceOnly": order.reduceOnly if order.reduceOnly is not None else False,
            "allOrNothing": False,
        }

        full_message = {
            "types": _types,
            "primaryType": "Order",
            "domain": self._domain_data,
            "message": message_data,
        }

        signable_message: SignableMessage = encode_typed_data(full_message=full_message)
        unsigned_hash = _hash_eip191_message(signable_message).hex()
        signed_message = self._account.signHash(unsigned_hash)
        return signed_message.signature.hex(), f"0x{unsigned_hash}"

    def get_order_hash(self, order: PlaceOrderInput) -> str:
        _, unsigned_hash = self.sign_order(order)
        return unsigned_hash
