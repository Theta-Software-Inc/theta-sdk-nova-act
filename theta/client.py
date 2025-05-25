from .session import Session
from .requests import make_request
from .settings import settings
from typing import Optional

class Client:
    """
    Client for the Theta Testing Engine
    """
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the client

        Args:
            api_key (str): The API authentication key
        """
        if api_key:
            settings.api_key = api_key
        
    async def get_sessions(self) -> list[Session]:
        """
        Get all previous sessions based on the API key

        Returns:
            list[Session]: A list of Session objects
        """
        url = f"{settings.base_url}/sessions/"
        response = await make_request(url, "GET", settings.api_key)
        return response["sessions"]
    
    async def get_evaluation_sets(self) -> list[str]:
        """
        Get all evaluation sets

        Returns:
            list[str]: A list of evaluation sets
        """
        url = f"{settings.base_url}/evaluation_sets/"
        response = await make_request(url, "GET", settings.api_key)
        return response["evaluation_sets"]
    
    async def create_session(self, name: str, env_type: str, eval_set: str) -> Session:
        """
        Create a new session

        Args:
            name (str): The name of the session
            env_type (str): The environment type
            eval_set (str): The evaluation set

        Returns:
            Session: The created session
        """
        url = f"{settings.base_url}/sessions/"
        response = await make_request(url, "POST", settings.api_key, {"name": name, "env_type": env_type, "eval_set": eval_set})
        return Session(name, response["id"], env_type, eval_set, response["tasks"])