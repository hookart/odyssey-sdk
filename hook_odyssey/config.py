from dataclasses import dataclass
from enum import Enum


@dataclass
class EIP712Domain:
    name: str
    version: str
    chain_id: int
    verifyingContract: str


@dataclass
class EnvironmentInfo:
    http_url: str
    ws_url: str
    domain: EIP712Domain


class Environment(Enum):
    TESTNET = EnvironmentInfo(
        http_url="https://goerli-api.hook.xyz/query",
        ws_url="wss://goerli-api.hook.xyz/query",
        domain=EIP712Domain(
            name="Hook",
            version="1.0.0",
            verifyingContract="0x64247BeF0C0990aF63FCbdd21dc07aC2b251f500",
            chain_id=46658378,
        ),
    )

    MAINNET = EnvironmentInfo(
        http_url="https://api-prod.hook.xyz/query",
        ws_url="wss://api-prod.hook.xyz/query",
        domain=EIP712Domain(
            name="Hook",
            version="1.0.0",
            verifyingContract="0xF9Bd1BaB25442A3b6888f2086736C6aC76A4Cf4B",
            chain_id=4665,
        ),
    )
