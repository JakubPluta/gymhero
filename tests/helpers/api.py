from typing import Any

from httpx import Response


def page_items(response: Response) -> list[dict[str, Any]]:
    return response.json()["items"]
