import httpx

from app.logger import enrich_context


class NotionClient:
    """Minimal async client to retrieve data from Notion"""

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
        }

    async def fetch_page(self, page_id: str) -> dict:
        log = enrich_context(event="notion_fetch", page_id=page_id)
        url = f"{self.base_url}/blocks/{page_id}/children"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                log.info("Fetched Notion page")
                return resp.json()
        except Exception as e:
            log.bind(error=str(e)).error("Failed to fetch Notion page")
            raise
