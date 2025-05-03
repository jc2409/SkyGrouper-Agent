import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerSse       
from agents.model_settings import ModelSettings
from agents import set_default_openai_key
from dotenv import load_dotenv

load_dotenv()               
set_default_openai_key(os.environ["OPENAI_API_KEY"])

MODEL_NAME = "gpt-4.1-2025-04-14" 

async def ask_agent(message: str) -> str:
    async with MCPServerSse(
        name="Python SSE Server",
        params={"url": "http://localhost:8000/sse"},
        client_session_timeout_seconds=30,
    ) as mcp_server:

        agent = Agent(
            model=MODEL_NAME,
            name="Assistant",
            instructions="Use the tools to help planning out user's trip",
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        result = await Runner.run(starting_agent=agent, input=message)
        return result.final_output
