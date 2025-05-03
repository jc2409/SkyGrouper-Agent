import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

import asyncio
import shutil
import subprocess
import time
from typing import Any
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv
from agents import set_default_openai_key
from flask import Flask, request
app = Flask(__name__)

@app.route('/generate', methods = ['GET','POST'])
async def run(mcp_server: MCPServer):
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    set_default_openai_key(api_key)
    agent = Agent(
        model="gpt-4.1-2025-04-14",
        name="Assistant",
        instructions="Use the tools to help planning out user's trip",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )
    
    message = "I am leaving from the London Gatwick Airport and will travel to Barcelona between July 7th 2025 and July 10th 2025. What would be the return ticket price for that? Recommend me some locations to stay as well my budget is under £800"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)
    
async def main():
    async with MCPServerSse(
        name="Python SSE Server",
        params={
            "url": "http://localhost:8000/sse",
        },
        client_session_timeout_seconds=30,
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