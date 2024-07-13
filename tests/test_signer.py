from copy import deepcopy
from decimal import Decimal

import pytest
from eth_account import Account
from eth_account.signers.base import BaseAccount
from web3 import Web3

from hook_odyssey.config import Environment
from hook_odyssey.signing import OdysseySigner
from hook_odyssey.types import (
    OrderDirection,
    OrderType,
    PlaceOrderInput,
    TimeInForce,
    from_decimal,
)


@pytest.fixture
def env():
    return Environment.MAINNET


@pytest.fixture
def private_key():
    return "0x28d9a28fc26c2ab04f5d9b662dbe3163211495df6f633bad17720656145e9cdc"


@pytest.fixture
def signer(env, private_key):
    return OdysseySigner(env, private_key)


@pytest.fixture
def sample_order():
    return PlaceOrderInput(
        marketHash="0x2227a28199b649ce2995eb8a1b0d2b36116b7e1dddb3622d85860dc717df4305",
        instrumentHash="0x194add7922e3fd9e6c17ca58efc31f97e6b891d13ea1919c751926daf98dd8a6",
        subaccount=37,
        orderType=OrderType.LIMIT,
        direction=OrderDirection.BUY,
        size=Decimal(1),
        limitPrice=Decimal(2),
        timeInForce=TimeInForce.GTC,
        nonce=0,
    )


@pytest.fixture
def expected_order_hash():
    return "0xe471301f9ec44a0a1b66f5b0e2b6f9f720cdfcfcfbb8d96bb92d6b8927a71566"


@pytest.fixture
def expected_order_signature():
    return "0x40fd267419f36e21c1955d18ae5e3cb1af3d866f35d5610b24e7fcd3275c694e785819d822e51d25af64a5de2767db787edd9cc6b576d7da0efcc53e258dc6721b"


def test_signer_initialization(signer, env, private_key):
    assert signer._env == env
    assert signer._private_key == private_key.removeprefix("0x")
    assert isinstance(signer._w3, Web3)
    assert isinstance(signer._account, BaseAccount)


def test_get_order_hash(signer, sample_order, expected_order_hash):
    order_hash = signer.get_order_hash(sample_order)
    assert isinstance(order_hash, str)
    assert order_hash.startswith("0x")
    assert len(order_hash) == 66  # 32 bytes (64 hex chars) + '0x'
    assert order_hash == expected_order_hash


def test_sign_order(
    signer, sample_order, expected_order_hash, expected_order_signature
):
    signature, unsigned_hash = signer.sign_order(sample_order)

    assert isinstance(signature, str)
    assert signature.startswith("0x")
    assert len(signature) == 132  # 65 bytes (130 hex chars) + '0x'
    assert signature == expected_order_signature

    assert isinstance(unsigned_hash, str)
    assert unsigned_hash.startswith("0x")
    assert len(unsigned_hash) == 66  # 32 bytes (64 hex chars) + '0x'
    assert unsigned_hash == expected_order_hash


def test_signature_verification(signer, sample_order):
    signature, unsigned_hash = signer.sign_order(sample_order)
    recovered_address = Account._recover_hash(unsigned_hash, signature=signature)
    assert recovered_address.lower() == signer._account.address.lower()


def test_different_orders_produce_different_hashes(signer, sample_order):
    hash1 = signer.get_order_hash(sample_order)

    # Create a slightly different order
    different_order = deepcopy(sample_order)
    different_order.size = str(from_decimal(Decimal(2)))

    hash2 = signer.get_order_hash(different_order)

    assert hash1 != hash2
    assert hash1 != hash2
