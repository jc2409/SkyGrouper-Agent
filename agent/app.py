import asyncio, json
import traceback
from datetime import date
from flask import Flask, request, jsonify
from shortlister import ShortlisterSync
from agent_helpers import ask_agent
from data_retrieve import get_data
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='http://localhost:5173')
scl = ShortlisterSync()

def _parse_iso(d: str) -> date:
    return date.fromisoformat(d)

def _validate_basics(js: dict) -> dict:
    # top-level required fields
    if "departures" not in js or "group_profiles" not in js \
       or "start_date" not in js or "end_date" not in js:
        raise KeyError("Must include: departures, group_profiles, start_date, end_date")

    # parse dates
    sd = _parse_iso(js["start_date"])
    ed = _parse_iso(js["end_date"])
    if ed <= sd:
        raise ValueError("'end_date' must be after 'start_date'")
    js["start_date"], js["end_date"] = sd, ed

    # each departure needs an airport code and budget
    for leg in js["departures"]:
        if "airport" not in leg or "budget" not in leg:
            raise KeyError("Each departure must have 'airport' and 'budget'")
    return js


PROMPT_TEMPLATE = """\
You are a travel-planning agent.

Return ONLY a JSON object exactly matching this schema (no markdown):

{{
  "destination": {{
    "city": {city},
    "country": "<country>",
    "summary": "<30-60 word engaging overview>",
    "top_highlights": ["<h1>", "<h2>", "<h3>"]
  }},
  "flights": [
    {{
      "departure_airport": "<IATA>",
      "airline": "<carrier>",
      "flight_no": "<code>",
      "outbound": {{
        "date": "<YYYY-MM-DD>",
        "time": "<HH:MM>",
        "price": <number>,
        "booking_link": "<https://…>"
      }},
      "return": {{
        "date": "<YYYY-MM-DD>",
        "time": "<HH:MM>",
        "price": <number>,
        "booking_link": "<https://…>"
      }}
    }}
  ],
  "totals": {{
    "total_flight_cost": <number>
  }}
}}

Use these inputs verbatim:

• Candidate city: {city}
• Travel dates: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}
• For each departure, note its airport and its individual budget.
• Group interests: {interests_list}

Ensure:
- No fields are omitted.
- Each flight’s return leg comes back to the same origin airport.
- Sum of all flight prices in `totals.total_flight_cost`.
- Stay within each origin’s budget.

Do NOT wrap in back-ticks or add any extra commentary.
"""


def _build_prompt(common: dict, city: str) -> str:
    # format departures as bullet list
    deps = "\n".join(
        f"- {leg['airport']}: budget ${leg['budget']}"
        for leg in common["departures"]
    )
    # flatten interests
    interests = ", ".join(
        interest 
        for profile in common["group_profiles"] 
        for interest in profile["interests"]
    )
    return PROMPT_TEMPLATE.format(
        city=city,
        start_date=common["start_date"],
        end_date=common["end_date"],
        interests_list=interests,
    ) + "\n\nDepartures:\n" + deps

async def _plan_for_all(common, candidates):
    tasks = []
    for c in candidates:
        prompt = _build_prompt(common, c["city"])
        tasks.append(ask_agent(prompt))
    raw = await asyncio.gather(*tasks)
    out = []
    for txt in raw:
        try:
            out.append(json.loads(txt))
        except json.JSONDecodeError as e:
            out.append({"raw": txt, "error": str(e)})
    return out

@app.post("/plan-trip")
def plan_trip():
    try:
        payload = get_data()
        data = _validate_basics(payload)
        shortlist = scl.get_shortlist(data["group_profiles"])
        candidates = shortlist["candidates"]
        plans = asyncio.run(_plan_for_all(data, candidates))
        return jsonify({ "plans": plans, "shortlist": candidates }), 200

    except Exception as exc:
        traceback.print_exc() 
        return jsonify(error=str(exc)), 500

if __name__ == "__main__":
    app.run(port=7000, debug=True)