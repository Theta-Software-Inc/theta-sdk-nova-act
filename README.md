# Theta SDK

This repo allows for testing of Amazon Nova Act in Theta's computer environments, with samples tasks selected from CUB (Computer Use Benchmark). At a high level, the SDK creates pre-configured environments for execution and evaluation of tasks, offering browser control via the Chrome DevTools Protocol (CDP).

---

## 1 · Prerequisites

• Python ≥ 3.9  
• Valid **Theta** and **Nova Act** API keys

Create a `.env` file in the project root:

```env
THETA_API_KEY=your_theta_key
NOVA_ACT_API_KEY=your_nova_act_key
```

## 2 · Install

```bash
uv venv .venv && source .venv/bin/activate    # create and activate venv
uv pip install -r pyproject.toml              # install requirements in venv
```

## 3 · Run the example

```bash
python example.py
```

1. **Create a new session and provision a browser environment**

   ```python
   session = await client.create_session(name="Example Run", env_type="browser", eval_set="cub_sample")
   env = await session.create_environment(task="flower_shop")
   ```

2. **Retrieve CDP URL to allow for Nova Act interaction, remote VNC URL for viewing and debugging**

   ```python
   cdp_url = await env.get_cdp_url() # CDP URL for Nova Act to interact with the environment
   remote_url = await env.get_remote_url() # VNC URL for remote access to the environment
   ```

3. **Start Nova Act interaction based on the task instruction and CDP URL from the environment**

   ```python
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
   ```

4. **Print the evaluation score (ranges from 0 to 1) and close the environment**
   ```python
   print("Evaluation score:", await env.evaluate())
   try:
       await env.close()
   except Exception as e:
       print(f"Warning: failed to close environment: {e}")
   ```

While running you will see:
• A remote VNC link you can open in your browser to watch the agent.
• A log file path (HTML) capturing each Nova Act step.

Use `example.py` as a starting point for your own experiments. This sample offers one basic example ("flower_shop") and two CUB tasks ("epa" + "interior_design").

Reach out to `founders@thetasoftware.ai` with questions or feedback.
