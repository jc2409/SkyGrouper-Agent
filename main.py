import asyncio
import os
import shutil
import subprocess
import time
from typing import Any
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv

load_dotenv()

async def run(mcp_server: MCPServer):
    agent = Agent(
        model="gpt-4.1-2025-04-14",
        name="Assistant",
        instructions="Use the tools to help planning out user's trip",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )
    
    message = "I am leaving from the London Gatwick Airport and will travel to Barcelona between July 7th 2025 and July 10th 2025. What would be the return ticket price for that?"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)
    
async def main():
    async with MCPServerSse(
        name="Python SSE Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        await run(server)
            
if __name__ == "__main__":
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed"
        )
        
    process: subprocess.Popen[Any] | None = None
    
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")
        print("Starting SSE Server at http://localhost:8000/sse ...")
        
        process = subprocess.Popen(["uv", "run", server_file])
        
        time.sleep(3)
        
        print("SSE server started. Running example... \n\n")
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)
        
    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()    