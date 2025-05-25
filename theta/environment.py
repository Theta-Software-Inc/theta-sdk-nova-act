from .requests import make_request
from .settings import settings
from pydantic import BaseModel
import time
import asyncio
import httpx

class Observation(BaseModel):
    """
    Observation class for the Theta Testing Engine
    """
    def __init__(self, screenshot: str, text: str) -> None:
        self.screenshot = screenshot
        self.text = text

class Environment:
    """
    Environment class for the Theta Testing Engine
    """
    def __init__(self, id: str, task: str, env_type: str) -> None:
        """
        Create a new environment, configured to the session it belongs to

        Args:
            session (Session): The session this environment belongs to
        """
        self.id = id
        self.task = task
        self.env_type = env_type
        self.current_observation = None
        self.cdp_url = None
        self.remote_url = None
        self.instruction = None

    async def step(self, action: list[str]) -> Observation:
        """
        Execute an action in the environment

        Args:
            action (list): The action to execute

        Returns:
            Observation: The observation of the environment
        """
        if self.env_type == "browser":
            raise NotImplementedError("Browser environments do not support step, use get_cdp_url() instead")
        url = f"{settings.base_url}/step/{self.id}/"
        response = await make_request(url, "POST", settings.api_key, {"action": action})
        self.current_observation = Observation(response["observation"])
        return self.current_observation
    
    async def get_cdp_url(self) -> str:
        """
        Get the CDP URL for the environment

        Returns:
            str: The CDP URL for the environment for Playwright-based agents
        """
        if self.env_type == "desktop":
            raise NotImplementedError("Desktop environments do not support get_cdp_url, use step() instead")
        url = f"{settings.base_url}/cdp/{self.id}/"
        response = await make_request(url, "GET", settings.api_key)
        self.cdp_url = response["cdp_url"]
        return self.cdp_url

    async def get_remote_url(self) -> str:
        """
        Get the remote VNC URL for the environment

        Returns:
            str: The VNC URL for remote access to the environment
        """
        url = f"{settings.base_url}/remote/{self.id}/"
        response = await make_request(url, "GET", settings.api_key)
        self.remote_url = response["remote_url"]
        return self.remote_url

    async def evaluate(self, timeout: int = 30) -> float:
        """
        Run the task-specific evaluation function

        Returns:
            float: The evaluation score
        """
        url = f"{settings.base_url}/evaluate/{self.id}/"
        start = time.monotonic()
        poll_interval = 2.0
        while True:
            try:
                response = await make_request(url, "GET", settings.api_key)
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                if time.monotonic() - start > timeout:
                    raise TimeoutError("Evaluation timed out (network)")
                await asyncio.sleep(poll_interval)
                continue
            if "score" in response:
                return response["score"]
            if response.get("status") == "pending":
                if time.monotonic() - start > timeout:
                    raise TimeoutError("Evaluation timed out (pending)")
                await asyncio.sleep(poll_interval)
                continue
            raise RuntimeError(f"Unexpected evaluate response: {response}")
    
    async def reset(self) -> Observation:
        """
        Reset the environment

        Returns:
            Observation: The initial observation of the environment
        """
        url = f"{settings.base_url}/reset/{self.id}/"
        response = await make_request(url, "POST", settings.api_key)
        self.current_observation = Observation(response["observation"])
        return self.current_observation

    async def close(self) -> None:
        """
        Close the environment
        """
        url = f"{settings.base_url}/close/{self.id}/"
        await make_request(url, "POST", settings.api_key)

    async def _wait_ready(self, timeout: int = 300):
        """Poll the backend until the environment status becomes 'ready'.

        Raises RuntimeError on backend error and TimeoutError when the
        timeout (seconds) is exceeded.
        """
        start = time.monotonic()
        while True:
            try:
                status_resp = await make_request(
                    f"{settings.base_url}/environments/{self.id}/status/",
                    "GET",
                    settings.api_key,
                )
            except (httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
                # Retry on network timeouts or transient 5xx server errors
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                    # For 4xx errors (client errors) re-raise immediately
                    raise
                await asyncio.sleep(2)
                if time.monotonic() - start > timeout:
                    raise TimeoutError("Environment provisioning timed out (network/server error)")
                continue
            status = status_resp.get("status")
            if status == "ready":
                return
            if status == "error":
                raise RuntimeError(status_resp.get("message", "Environment provisioning failed"))
            await asyncio.sleep(2)
