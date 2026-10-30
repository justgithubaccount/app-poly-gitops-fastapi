import pytest

from app.integrations.behavior_manager import BehaviorManager


class FakeNotionClient:
    async def fetch_page(self, page_id: str) -> dict:
        assert page_id == "page-id"
        return {
            "results": [
                {
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {"plain_text": "agents:\n  - role: reviewer\ntasks: []\n"}
                        ]
                    },
                }
            ]
        }


@pytest.mark.asyncio
async def test_optional_behavior_manager_parses_notion_yaml() -> None:
    manager = BehaviorManager(FakeNotionClient(), "page-id")

    await manager.refresh()

    assert manager.behavior is not None
    assert manager.behavior.agents[0].role == "reviewer"
