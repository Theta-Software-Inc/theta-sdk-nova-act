import httpx
from typing import Any, Optional

async def make_request(url: str, method: str, api_key: Optional[str] = None, data: Optional[Any] = None) -> dict:
    """
    Make a request to the Theta Testing Engine API

    Args:
        url (str): The URL to make the request to
        method (str): The HTTP method to use
        api_key (Optional[str]): The API key to use
        data (Optional[Any]): The data to send with the request

    Returns:
        dict: The response from the API

    Raises:
        ValueError: If the API key is missing
    """
    if not api_key:
        raise ValueError("API key is missing")
        
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
