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

PROMPT_TEMPLATE = """\
You are a travel-planning agent.

Return ONLY a valid JSON object that matches *exactly* this schema
(no markdown, no stray text before or after):

{{
  "destination": {{
    "city": "{destination_city}",
    "country": "<country name>",
    "summary": "<30-60-word engaging overview of the destination>",
    "top_highlights": [
      "<main highlight 1>",
      "<main highlight 2>",
      "<main highlight 3>"
    ]
  }},
  "flights": {{
    "total_price": <number>,
    "airline": "<carrier name>",
    "outbound": {{
      "date": "<YYYY-MM-DD>",
      "time": "<HH:MM>",
      "flight_no": "<code>",
      "from": "<IATA>",
      "to": "<IATA>",
      "price": <number>,
      "booking_link": "<https://…>"
    }},
    "return": {{
      "date": "<YYYY-MM-DD>",
      "time": "<HH:MM>",
      "flight_no": "<code>",
      "from": "<IATA>",
      "to": "<IATA>",
      "price": <number>,
      "booking_link": "<https://…>"
    }}
  }},
  "accommodations": [
    {{
      "name": "<hotel | airbnb>",
      "platform": "<Booking.com | Airbnb | …>",
      "total_price": <number>,
      "price_per_night": <number>,
      "location": "<neighbourhood>",
      "why": "<one-sentence reason>",
      "booking_link": "<https://…>"
    }}
    // up to 3 options
  ],
  "grand_totals": [
    {{ "option_index": 0, "total_trip_cost": <number> }},
    {{ "option_index": 1, "total_trip_cost": <number> }},
    {{ "option_index": 2, "total_trip_cost": <number> }}
  ]
}}

Fill every required field; omit none. Use the budget and dates below:

• Departure airport: {departure_airport}
• Destination city: {destination_city}
• Start date: {start_date:%Y-%m-%d}
• End date:   {end_date:%Y-%m-%d}
• Budget:     {budget}

Do NOT wrap the JSON in back-ticks or add commentary.
"""

def build_prompt(data: dict) -> str:
    return PROMPT_TEMPLATE.format(**data)