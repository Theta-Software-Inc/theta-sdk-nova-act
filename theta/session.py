from .environment import Environment
from .requests import make_request
from .settings import settings
class Session:
    """
    Session class for the Theta Testing Engine
    """
    def __init__(self, name: str, id: str, env_type: str, eval_set: str, tasks: list[str]) -> None:
        """
        Create a new evaluation

        Args:
            name (str): The name of the session
            id (str): The ID of the session
            env_type (str): The environment type
            eval_set (str): The evaluation set
            tasks (list[str]): The tasks to run in the session
        """
        self.name = name
        self.id = id
        self.env_type = env_type
        self.eval_set = eval_set
        self.tasks = tasks
        self.environments = []

    async def create_environment(self, task: str, wait: bool = True) -> Environment:
        """Create a new environment.

        Args:
            task: The task to run in the environment
            wait: When True (default), block until the environment status becomes
                "ready" on the backend so callers receive an immediately usable
                `Environment` instance. If False, the caller is responsible for
                checking readiness.
        """
        url = f"{settings.base_url}/environments/"
        response = await make_request(url, "POST", settings.api_key, {"session_id": self.id, "env_type": self.env_type, "task_id": task})
        environment = Environment(response["id"], task, self.env_type)
        if self.env_type == "browser":
            environment.instruction = response["instruction"]
        if wait:
            await environment._wait_ready()
        self.environments.append(environment)
        return environment
    
    async def get_environments(self) -> list[Environment]:
        """
        Get all running environments for the session
        """
        url = f"{settings.base_url}/environments/"
        response = await make_request(url, "GET", settings.api_key, {"session_id": self.id})
        return response["environments"]