from typing import AsyncGenerator, List, Optional

from .config import Environment
from .exceptions import APIKeyError, OdysseyAPIError, PrivateKeyError
from .graphql import GraphQLClient
from .signing import OdysseySigner
from .types import (
    AccountDetails,
    BBOEvent,
    OrderbookEvent,
    PerpetualPair,
    PlaceOrderInput,
    SignatureInput,
    SignatureType,
    StatisticsEvent,
    SubaccountBalanceEvent,
    SubaccountOrderEvent,
    SubaccountPositionEvent,
    TickerEvent,
    TransferHistory,
    TransferType,
)


class OdysseyClient:
    def __init__(
        self,
        env: Environment,
        api_key: Optional[str] = None,
        private_key: Optional[str] = None,
    ):
        self._env = env
        self._api_key = api_key
        self._private_key = private_key
        if self._private_key:
            self._signer = OdysseySigner(env, self._private_key)
        self._graphql_client = GraphQLClient(env.value.http_url, env.value.ws_url)

    # Subscriptions
    async def subscribe_ticker(self, symbol: str) -> AsyncGenerator[TickerEvent, None]:
        query = """
        subscription getTicker($symbol: String!) {
            ticker(symbol: $symbol) {
                price
                timestamp
            }
        }
        """
        variables = {"symbol": symbol}
        async for event in self._graphql_client.subscribe(query, variables):
            yield TickerEvent(**event["ticker"])

    async def subscribe_statistics(
        self, symbol: str
    ) -> AsyncGenerator[StatisticsEvent, None]:
        query = """
            subscription onStatisticsEvent($symbol: String!) {
                statistics(symbol: $symbol) {
                    eventType
                    timestamp
                    fundingRateBips
                    nextFundingEpoch
                }
            }
        """
        variables = {"symbol": symbol}
        async for event in self._graphql_client.subscribe(query, variables):
            yield StatisticsEvent(**event["statistics"])

    async def subscribe_bbo(
        self, symbol: str, instrument_type: str = "PERPETUAL"
    ) -> AsyncGenerator[BBOEvent, None]:
        query = """
            subscription onBboEvent($symbol: String!, $instrumentType: InstrumentType!) {
                bbo(symbol: $symbol, instrumentType: $instrumentType) {
                    eventType
                    timestamp
                    instruments {
                        id
                        markPrice
                    }
                }
            }
        """
        variables = {"symbol": symbol, "instrumentType": instrument_type}
        async for event in self._graphql_client.subscribe(query, variables):
            yield BBOEvent(**event["bbo"])

    async def subscribe_orderbook(
        self, instrument_hash: str
    ) -> AsyncGenerator[OrderbookEvent, None]:
        query = """
            subscription onOrderbookEvent($instrumentHash: ID!) {
                orderbook(instrumentHash: $instrumentHash) {
                    eventType
                    timestamp
                    bidLevels {
                        direction
                        size
                        price
                    }
                    askLevels {
                        direction
                        size
                        price
                    }
                }
            }
        """
        variables = {"instrumentHash": instrument_hash}
        async for event in self._graphql_client.subscribe(query, variables):
            yield OrderbookEvent(**event["orderbook"])

    async def subscribe_subaccount_orders(
        self, subaccount: str
    ) -> AsyncGenerator[SubaccountOrderEvent, None]:
        if not self._api_key:
            raise APIKeyError("No API key provided")

        query = """
            subscription onSubaccountOrderEvent($subaccount: BigInt!) {
                subaccountOrders(subaccount: $subaccount) {
                    eventType
                    orders {
                        instrument {
                            id
                        }
                        direction
                        size
                        remainingSize
                        orderHash
                        status
                        orderType
                        limitPrice
                    }
                }
            }
        """
        variables = {"subaccount": subaccount}
        async for event in self._graphql_client.subscribe(query, variables):
            yield SubaccountOrderEvent(**event["subaccountOrders"])

    async def subscribe_subaccount_balances(
        self, address: str
    ) -> AsyncGenerator[SubaccountBalanceEvent, None]:
        if not self._api_key:
            raise APIKeyError("No API key provided")

        query = """
            subscription onSubaccountBalanceEvent($address: Address!) {
                subaccountBalances(address: $address) {
                    eventType
                    balances {
                        subaccount
                        subaccountID
                        balance
                        assetName
                    }
                }
            }
        """
        variables = {"address": address}
        async for event in self._graphql_client.subscribe(query, variables):
            yield SubaccountBalanceEvent(**event["subaccountBalances"])

    async def subscribe_subaccount_positions(
        self, address: str
    ) -> AsyncGenerator[SubaccountPositionEvent, None]:
        if not self._api_key:
            raise APIKeyError("No API key provided")

        query = """
            subscription onSubaccountPositionEvent($address: Address!) {
                subaccountPositions(address: $address) {
                    eventType
                    positions {
                        instrument {
                            id
                        }
                        subaccount
                        marketHash
                        sizeHeld
                        isLong
                        averageCost
                    }
                }
            }
        """
        variables = {"address": address}
        async for event in self._graphql_client.subscribe(query, variables):
            yield SubaccountPositionEvent(**event["subaccountPositions"])

    # Market Info
    async def perpetual_pairs(self) -> List[PerpetualPair]:
        query = """
            query PerpetualPairs {
                perpetualPairs {
                    marketHash
                    instrumentHash
                    symbol
                    baseCurrency
                    minOrderSize
                    maxOrderSize
                    minOrderSizeIncrement
                    minPriceIncrement
                    initialMarginBips
                    preferredSubaccount
                    subaccount
                }
            }
        """
        try:
            result = await self._graphql_client.execute(query)
        except Exception:
            raise OdysseyAPIError

        pairs = []
        for pair_data in result["perpetualPairs"]:
            pair = PerpetualPair(**pair_data)
            pairs.append(pair)
        return pairs

    # Account Info
    async def account_details(self) -> AccountDetails:
        if not self._api_key:
            raise APIKeyError("No API key provided")

        query = """
            query AccountDetails {
                accountDetails {
                    tier
                    makerFeeBips
                    takerFeeBips
                }
            }
        """
        try:
            result = await self._graphql_client.execute(query)
        except Exception:
            raise OdysseyAPIError
        return AccountDetails(**result["accountDetails"])

    # Place Order
    async def place_order(self, order: PlaceOrderInput):
        if not self._api_key:
            raise APIKeyError("No API key provided")
        if not self._private_key or not self._signer:
            raise PrivateKeyError("No private key provided")

        raw_signature, _ = self._signer.sign_order(order)
        signature = SignatureInput(
            signatureType=SignatureType.DIRECT,
            signature=raw_signature,
        )

        mutation = """
            mutation PlaceOrder(
                $orderInput: PlaceOrderInput!
                $signature: SignatureInput!
            ) {
                placeOrderV2(
                    orderInput: $orderInput
                    signature: $signature
                )
            }
        """
        variables = {"orderInput": order, "signature": signature}
        try:
            await self._graphql_client.execute(mutation, variables)
        except Exception:
            raise OdysseyAPIError

    # Cancel Order
    async def cancel_order(self, order_hash: str) -> bool:
        mutation = """
            mutation CancelOrder($orderHash: String!) {
                cancelOrderV2(orderHash: $orderHash)
            }
        """
        variables = {"orderHash": order_hash}
        try:
            result = await self._graphql_client.execute(
                query=mutation, variables=variables
            )
        except Exception:
            raise OdysseyAPIError
        return result.get("cancelOrderV2", False)

    # Transfer History
    async def transfer_history(
        self,
        subaccount: str,
        market_hash: Optional[str] = None,
        trasfer_type: Optional[TransferType] = None,
        cursor: Optional[str] = None,
    ) -> TransferHistory:
        if not self._api_key:
            raise APIKeyError("No API key provided")

        query = """
            query TransferHistory(
                $subaccount: BigInt!
                $marketHash: String
                $transferType: TransferType
                $cursor: String
            ) {
                transferHistory(
                    subaccount: $subaccount
                    marketHash: $marketHash
                    transferType: $transferType
                    cursor: $cursor
                ) {
                    data {
                        transactionHash
                        name
                        symbol
                        type
                        subaccount
                        amount
                        price
                        fees
                        baseCurrency
                        fundingRate
                        isShort
                        timestamp
                    }
                    cursor
                }
            }
        """
        variables = {
            "subaccount": subaccount,
            "marketHash": market_hash,
            "transferType": trasfer_type.value if trasfer_type else None,
            "cursor": cursor,
        }
        try:
            result = await self._graphql_client.execute(query, variables)
        except Exception:
            raise OdysseyAPIError
        return TransferHistory(**result["transferHistory"])
