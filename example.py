from theta import Client
from nova_act import NovaAct
from nova_act.types.act_errors import ActError
import asyncio
import os
from pathlib import Path

# Load environment variables from local .env file if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for _line in env_path.read_text().splitlines():
        if _line.strip() and not _line.startswith("#") and "=" in _line:
            k, v = _line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# initialize client
client = Client()

async def main() -> None:
    # Sessions allow for longer-term statistics tracking across multiple environments and task runs. For this sample, you can simply create a new session for every task.
    # For Nova Act, we want a browser-based environment.
    session = await client.create_session(name="Example Run", env_type="browser", eval_set="cub_sample")
    print("Session created.")

    # List all available tasks: "flower_shop" is a simple example task, and "epa" + "interior_design" are sample tasks from the CUB benchmark.
    tasks = session.tasks
    print("Available tasks: ", tasks)

    # Create an environment for the task, configured to the "".
    # Environments currently take ~1 minute to provision on cold starts, but this time will be dramatically reduced on our full release.
    print("Creating environment...")
    env = await session.create_environment(task="flower_shop")

    # Get the CDP URL for the environment. This is how Nova Act will interact with the environment.
    cdp_url = await env.get_cdp_url()

    # Get the remote VNC URL for the environment. Use this URL in the browser to view and interact with the environment yourself.
    remote_url = await env.get_remote_url()

    # Information about the environment
    print("Environment ID: ", env.id)
    print("Task instruction: ", env.instruction)
    print("Remote VNC URL: ", remote_url)

    # Run Nova Act in a separate thread because it uses Playwright Sync API (not compatible with running inside an asyncio loop)
    def run_nova():
        with NovaAct(
            starting_page="https://www.google.com",
            cdp_endpoint_url=cdp_url,
        ) as nova:
            try:
                nova.act(env.instruction)
            except ActError as e:
                print(f"Nova Act failed: {e}")
            except Exception as e:
                print(f"Unexpected Nova Act error: {e}")

    await asyncio.to_thread(run_nova)

    # Evaluate the environment based on correctness, with a score between 0 and 1.
    # input("Press Enter to evaluate...")
    print("Evaluation score: ", await env.evaluate())
    # input("Press Enter to close the environment...")
    try:
        await env.close()
        print("Environment closed.")
    except Exception as e:
        print(f"Warning: failed to close environment: {e}")

if __name__ == "__main__":
    asyncio.run(main())