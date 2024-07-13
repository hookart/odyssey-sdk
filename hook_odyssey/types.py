from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    SNAPSHOT = "SNAPSHOT"
    UPDATE = "UPDATE"


class OrderDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"


class PriceLevelDirection(Enum):
    BID = "BID"
    ASK = "ASK"


class OrderStatus(Enum):
    OPEN = "OPEN"
    PARTIALLY_MATCHED = "PARTIALLY_MATCHED"
    MATCHED = "MATCHED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    UNFILLABLE = "UNFILLABLE"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class RewardsTier(Enum):
    TIER_BASE = "TIER_BASE"  # Iron
    TIER_1 = "TIER_1"  # Bronze
    TIER_2 = "TIER_2"  # Silver
    TIER_3 = "TIER_3"  # Gold
    TIER_4 = "TIER_4"  # Placeholder for potential future tier


class BaseCurrency(Enum):
    ETH = "ETH"
    USDC = "USDC"


class TimeInForce(Enum):
    GTC = "GTC"
    GTD = "GTD"


class SignatureType(Enum):
    DIRECT = "DIRECT"
    SIGNING_KEY = "SIGNING_KEY"
    SIGNING_KEY_CACHED = "SIGNING_KEY_CACHED"
    EIP1271 = "EIP1271"


class TransferType(Enum):
    TRANSFER = "TRANSFER"
    TRADE = "TRADE"
    FUNDING = "FUNDING"
    SETTLEMENT = "SETTLEMENT"
    LIQUIDATION = "LIQUIDATION"


def from_decimal(value: Decimal) -> int:
    """
    Convert a Decimal value to a uint256 integer value with 18 decimal places of precision.

    Example:
        from_decimal(Decimal('1.5')) returns 1500000000000000000
    """
    return int(value * Decimal(10**18))


def to_decimal(value: int) -> Decimal:
    """
    Convert a uint256 integer value with 18 decimal places of precision to a Decimal value.

    Example:
        to_decimal(1500000000000000000) returns Decimal('1.5')
    """
    return Decimal(value) / Decimal(10**18)


## Note: lower camel case is used for the dataclass field names to match JSON api responses


@dataclass
class TickerEvent:
    price: Decimal
    timestamp: int

    def __init__(self, price: str, timestamp: int):
        try:
            self.price = to_decimal(int(price))
        except ValueError:
            raise ValueError(f"Invalid price: {price}")
        self.timestamp = timestamp


@dataclass
class StatisticsEvent:
    eventType: EventType
    timestamp: int
    fundingRateBips: int
    nextFundingEpoch: int

    def __init__(
        self,
        eventType: str,
        timestamp: int,
        fundingRateBips: int,
        nextFundingEpoch: int,
    ):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.timestamp = timestamp
        self.fundingRateBips = fundingRateBips
        self.nextFundingEpoch = nextFundingEpoch


@dataclass
class Instrument:
    id: str
    markPrice: Optional[Decimal]

    def __init__(self, id: str, markPrice: Optional[str] = None):
        self.id = id
        if markPrice is not None:
            try:
                self.markPrice = to_decimal(int(markPrice))
            except ValueError:
                raise ValueError(f"Invalid markPrice: {markPrice}")
        else:
            self.markPrice = None


@dataclass
class BBOEvent:
    eventType: EventType
    timestamp: int
    instruments: List[Instrument]

    def __init__(self, eventType: str, timestamp: int, instruments: List[dict]):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.timestamp = timestamp
        self.instruments = [Instrument(**inst) for inst in instruments]


@dataclass
class PriceLevel:
    direction: PriceLevelDirection
    size: Decimal
    price: Decimal

    def __init__(self, direction: str, size: str, price: str):
        try:
            self.direction = PriceLevelDirection(direction)
        except ValueError:
            raise ValueError(f"Invalid direction: {direction}")
        try:
            self.size = to_decimal(int(size))
        except ValueError:
            raise ValueError(f"Invalid size: {size}")
        try:
            self.price = to_decimal(int(price))
        except ValueError:
            raise ValueError(f"Invalid price: {price}")


@dataclass
class OrderbookEvent:
    eventType: EventType
    timestamp: int
    bidLevels: List[PriceLevel]
    askLevels: List[PriceLevel]

    def __init__(
        self,
        eventType: str,
        timestamp: int,
        bidLevels: List[dict],
        askLevels: List[dict],
    ):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.timestamp = timestamp
        self.bidLevels = [PriceLevel(**level) for level in bidLevels]
        self.askLevels = [PriceLevel(**level) for level in askLevels]


@dataclass
class Order:
    instrument: Instrument
    direction: OrderDirection
    size: Decimal
    remainingSize: Decimal
    orderHash: str
    status: OrderStatus
    orderType: OrderType
    limitPrice: Optional[Decimal]

    def __init__(
        self,
        instrument: dict,
        direction: str,
        size: str,
        remainingSize: str,
        orderHash: str,
        status: str,
        orderType: str,
        limitPrice: Optional[str] = None,
    ):
        self.instrument = Instrument(**instrument)
        try:
            self.direction = OrderDirection(direction)
        except ValueError:
            raise ValueError(f"Invalid direction: {direction}")
        try:
            self.size = to_decimal(int(size))
        except ValueError:
            raise ValueError(f"Invalid size: {size}")
        try:
            self.remainingSize = to_decimal(int(remainingSize))
        except ValueError:
            raise ValueError(f"Invalid remainingSize: {remainingSize}")
        self.orderHash = orderHash
        try:
            self.status = OrderStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}")
        try:
            self.orderType = OrderType(orderType)
        except ValueError:
            raise ValueError(f"Invalid orderType: {orderType}")
        if limitPrice is not None:
            try:
                self.limitPrice = to_decimal(int(limitPrice))
            except ValueError:
                raise ValueError(f"Invalid limitPrice: {limitPrice}")
        else:
            self.limitPrice = None


@dataclass
class SubaccountOrderEvent:
    eventType: EventType
    orders: List[Order]

    def __init__(self, eventType: str, orders: List[dict]):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.orders = [Order(**order) for order in orders]


@dataclass
class Balance:
    subaccount: int
    subaccountID: int
    balance: Decimal
    assetName: str

    def __init__(
        self, subaccount: str, subaccountID: int, balance: str, assetName: str
    ):
        try:
            self.subaccount = int(subaccount)
        except ValueError:
            raise ValueError(f"Invalid subaccount: {subaccount}")
        self.subaccountID = subaccountID
        try:
            self.balance = to_decimal(int(balance))
        except ValueError:
            raise ValueError(f"Invalid balance: {balance}")
        self.assetName = assetName


@dataclass
class SubaccountBalanceEvent:
    eventType: EventType
    balances: List[Balance]

    def __init__(self, eventType: str, balances: List[dict]):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.balances = [Balance(**balance) for balance in balances]


@dataclass
class Position:
    instrument: Instrument
    subaccount: int
    marketHash: str
    sizeHeld: Decimal
    isLong: bool
    averageCost: Decimal

    def __init__(
        self,
        instrument: dict,
        subaccount: str,
        marketHash: str,
        sizeHeld: str,
        isLong: bool,
        averageCost: str,
    ):
        self.instrument = Instrument(**instrument)
        self.subaccount = int(subaccount)
        self.marketHash = marketHash
        try:
            self.sizeHeld = to_decimal(int(sizeHeld))
        except ValueError:
            raise ValueError(f"Invalid sizeHeld: {sizeHeld}")
        self.isLong = isLong
        try:
            self.averageCost = to_decimal(int(averageCost))
        except ValueError:
            raise ValueError(f"Invalid averageCost: {averageCost}")


@dataclass
class SubaccountPositionEvent:
    eventType: EventType
    positions: List[Position]

    def __init__(self, eventType: str, positions: List[dict]):
        try:
            self.eventType = EventType(eventType)
        except ValueError:
            raise ValueError(f"Invalid eventType: {eventType}")
        self.positions = [Position(**position) for position in positions]


@dataclass
class PerpetualPair:
    marketHash: str
    instrumentHash: str
    symbol: str
    baseCurrency: BaseCurrency
    minOrderSize: Decimal
    maxOrderSize: Decimal
    minOrderSizeIncrement: Decimal
    minPriceIncrement: Decimal
    initialMarginBips: int
    preferredSubaccount: int
    subaccount: Optional[int]

    def __init__(
        self,
        marketHash: str,
        instrumentHash: str,
        symbol: str,
        baseCurrency: str,
        minOrderSize: str,
        maxOrderSize: str,
        minOrderSizeIncrement: str,
        minPriceIncrement: str,
        initialMarginBips: int,
        preferredSubaccount: int,
        subaccount: Optional[str] = None,
    ):
        self.marketHash = marketHash
        self.instrumentHash = instrumentHash
        self.symbol = symbol
        try:
            self.baseCurrency = BaseCurrency(baseCurrency)
        except ValueError:
            raise ValueError(f"Invalid baseCurrency: {baseCurrency}")
        try:
            self.minOrderSize = to_decimal(int(minOrderSize))
        except ValueError:
            raise ValueError(f"Invalid minOrderSize: {minOrderSize}")
        try:
            self.maxOrderSize = to_decimal(int(maxOrderSize))
        except ValueError:
            raise ValueError(f"Invalid maxOrderSize: {maxOrderSize}")
        try:
            self.minOrderSizeIncrement = to_decimal(int(minOrderSizeIncrement))
        except ValueError:
            raise ValueError(f"Invalid minOrderSizeIncrement: {minOrderSizeIncrement}")
        try:
            self.minPriceIncrement = to_decimal(int(minPriceIncrement))
        except ValueError:
            raise ValueError(f"Invalid minPriceIncrement: {minPriceIncrement}")
        self.initialMarginBips = initialMarginBips
        self.preferredSubaccount = preferredSubaccount
        if subaccount is not None:
            try:
                self.subaccount = int(subaccount)
            except ValueError:
                raise ValueError(f"Invalid subaccount: {subaccount}")
        else:
            self.subaccount = None


@dataclass
class AccountDetails:
    tier: RewardsTier
    makerFeeBips: int
    takerFeeBips: int

    def __init__(self, tier: str, makerFeeBips: int, takerFeeBips: int):
        try:
            self.tier = RewardsTier(tier)
        except ValueError:
            raise ValueError(f"Invalid tier: {tier}")
        self.makerFeeBips = makerFeeBips
        self.takerFeeBips = takerFeeBips


@dataclass
class PlaceOrderInput:
    marketHash: str
    instrumentHash: str
    subaccount: str  # BigInts are represented as strings for go marshalling
    orderType: OrderType
    direction: OrderDirection
    size: str  # BigInts are represented as strings for go marshalling
    limitPrice: Optional[str]  # BigInts are represented as strings for go marshalling
    volatilityBips: Optional[int]
    timeInForce: TimeInForce
    expiration: Optional[int]
    nonce: str  # BigInts are represented as strings for go marshalling
    postOnly: Optional[bool]
    reduceOnly: Optional[bool]

    def __init__(
        self,
        marketHash: str,
        instrumentHash: str,
        subaccount: int,
        orderType: OrderType,
        direction: OrderDirection,
        size: Decimal,
        timeInForce: TimeInForce,
        nonce: int,
        limitPrice: Optional[Decimal] = None,
        volatilityBips: Optional[int] = None,
        expiration: Optional[int] = None,
        postOnly: bool = False,
        reduceOnly: bool = False,
    ):
        self.marketHash = marketHash
        self.instrumentHash = instrumentHash
        self.subaccount = str(subaccount)
        self.orderType = orderType
        self.direction = direction
        self.size = str(from_decimal(size))
        self.timeInForce = timeInForce
        self.nonce = str(nonce)
        if limitPrice is not None:
            try:
                self.limitPrice = str(from_decimal(limitPrice))
            except ValueError:
                raise ValueError(f"Invalid limitPrice: {limitPrice}")
        else:
            self.limitPrice = None
        if volatilityBips is not None:
            try:
                self.volatilityBips = volatilityBips
            except ValueError:
                raise ValueError(f"Invalid volatilityBips: {volatilityBips}")
        else:
            self.volatilityBips = None
        if expiration is not None:
            try:
                self.expiration = expiration
            except ValueError:
                raise ValueError(f"Invalid expiration: {expiration}")
        else:
            self.expiration = None
        self.postOnly = postOnly
        self.reduceOnly = reduceOnly

    def to_dict(self):
        d = {
            "marketHash": self.marketHash,
            "instrumentHash": self.instrumentHash,
            "subaccount": self.subaccount,
            "orderType": self.orderType.value,
            "direction": self.direction.value,
            "size": self.size,
            "timeInForce": self.timeInForce.value,
            "nonce": self.nonce,
            "postOnly": self.postOnly,
            "reduceOnly": self.reduceOnly,
        }
        if self.limitPrice is not None:
            d["limitPrice"] = self.limitPrice
        if self.volatilityBips is not None:
            d["volatilityBips"] = self.volatilityBips
        if self.expiration is not None:
            d["expiration"] = self.expiration
        return d


@dataclass
class SigningKeyInput:
    signer: str
    authorizer: str
    expiration: int
    chainID: int


@dataclass
class SignatureInput:
    signatureType: SignatureType
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signatureType": self.signatureType.value,
            "signature": self.signature,
        }


@dataclass
class TransferHistoryItem:
    transactionHash: str
    name: str
    symbol: str
    transferType: TransferType  # "type" is a reserved keyword in Python
    subaccount: int
    amount: int
    price: int
    fees: int
    baseCurrency: BaseCurrency
    fundingRate: int
    isShort: bool
    timestamp: int

    def __init__(
        self,
        transactionHash: str,
        name: str,
        symbol: str,
        transferType: str,
        subaccount: int,
        amount: int,
        price: int,
        fees: int,
        baseCurrency: str,
        fundingRate: int,
        isShort: bool,
        timestamp: int,
    ):
        self.transactionHash = transactionHash
        self.name = name
        self.symbol = symbol
        try:
            self.transferType = TransferType(transferType)
        except ValueError:
            raise ValueError(f"Invalid transferType: {transferType}")
        self.subaccount = subaccount
        self.amount = amount
        self.price = price
        self.fees = fees
        try:
            self.baseCurrency = BaseCurrency(baseCurrency)
        except ValueError:
            raise ValueError(f"Invalid baseCurrency: {baseCurrency}")
        self.fundingRate = fundingRate
        self.isShort = isShort
        self.timestamp = timestamp


@dataclass
class TransferHistory:
    data: List[TransferHistoryItem]
    cursor: str

    def __init__(self, data: List[dict], cursor: str):
        self.data = [TransferHistoryItem(**item) for item in data]
        self.cursor = cursor
