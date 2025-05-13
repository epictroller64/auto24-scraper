import httpx
import asyncio

class NetworkService:

    def __init__(self, retry_count: int = 3, retry_delay_s: int = 3000) -> None:
        self.retry_count = retry_count
        self.retry_delay_ms = retry_delay_s

    async def get_request(self, url: str):
        """
        Initiate request which is then queued or processed immediately
        """
        async with httpx.AsyncClient() as client:
            retry_count = 0
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.text
                return data
            except httpx.HTTPStatusError as e:
                if retry_count == self.retry_count:
                    raise e
                await asyncio.sleep(self.retry_delay_ms)
                retry_count+=1
            except Exception as e:
                raise e
