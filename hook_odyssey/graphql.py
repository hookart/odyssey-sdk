from typing import Any, AsyncGenerator, Dict, Optional

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport


class GraphQLClient:
    def __init__(self, http_url: str, ws_url: str):
        self._http_client = Client(
            transport=AIOHTTPTransport(url=http_url),
            fetch_schema_from_transport=False,
        )
        self._ws_client = Client(transport=WebsocketsTransport(url=ws_url))

    async def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        async with self._http_client as session:
            return await session.execute(gql(query), variable_values=variables)

    async def subscribe(
        self, subscription_query: str, variables: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        async with self._ws_client as session:
            subscription = gql(subscription_query)
            async for result in session.subscribe(
                subscription, variable_values=variables
            ):
                yield result
