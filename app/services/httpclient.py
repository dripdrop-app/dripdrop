from contextlib import asynccontextmanager

import httpx


@asynccontextmanager
async def AsyncClient():
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=3), follow_redirects=True
    ) as client:
        yield client
