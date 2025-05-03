import asyncio, json
from datetime import date
from flask import Flask, request, jsonify
from shortlister import ShortlisterSync
from agent_helpers import ask_agent

app = Flask(__name__)
scl = ShortlisterSync()

def _parse_iso(d: str) -> date:
    return date.fromisoformat(d)

def _validate_basics(js: dict) -> dict:
    required = ["group_profiles", "departure_airport",
                "start_date", "end_date", "budget"]
    missing = [k for k in required if k not in js]
    if missing:
        raise KeyError(f"Missing: {', '.join(missing)}")

    sd, ed = _parse_iso(js["start_date"]), _parse_iso(js["end_date"])
    if ed <= sd:
        raise ValueError("'end_date' must be after 'start_date'")

    js["start_date"] = sd
    js["end_date"]   = ed
    return js

PROMPT_TEMPLATE = """\
You are a travel-planning agent.

Return ONLY a valid JSON object that matches *exactly* this schema
(no markdown, no stray text before or after):

{{
  "destination": {{
    "city": "{city}",
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
• Destination city: {city}
• Start date: {start_date:%Y-%m-%d}
• End date:   {end_date:%Y-%m-%d}
• Budget:     {budget}

Do NOT wrap the JSON in back-ticks or add commentary.
"""

def _build_prompt(common: dict, city: str) -> str:
    return PROMPT_TEMPLATE.format(
        city=city,
        departure_airport=common["departure_airport"],
        start_date=common["start_date"],
        end_date=common["end_date"],
        budget=common["budget"],
    )

async def _plan_for_all(common, candidates):
    """Run 4 agent calls concurrently and collect their JSON outputs."""
    tasks = []
    for c in candidates:
        prompt = _build_prompt(common, c["city"])
        tasks.append(ask_agent(prompt))          # this returns str

    raw_outputs = await asyncio.gather(*tasks)

    results = []
    for txt in raw_outputs:
        try:
            results.append(json.loads(txt))
        except json.JSONDecodeError as e:
            results.append({"raw": txt, "error": str(e)})
    return results

@app.post("/plan-trip")
def plan_trip():
    try:
        payload = request.get_json(force=True)
        data = _validate_basics(payload)
    except Exception as exc:
        status = 400 if isinstance(exc, (KeyError, ValueError)) else 500
        return jsonify(error=str(exc)), status

    # ---------- 1. shortlist ----------
    try:
        shortlist = scl.get_shortlist(data["group_profiles"])
        candidates = shortlist["candidates"]          # list[dict]
    except Exception as exc:
        return jsonify(error=f"Short-listing failed: {exc}"), 500

    # ---------- 2. detailed plans ----------
    try:
        plans = asyncio.run(_plan_for_all(data, candidates))
    except Exception as exc:
        return jsonify(error=f"Planning agent failed: {exc}"), 500

    # ---------- 3. bundle & reply ----------
    return jsonify({
        "plans": plans   
    }), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)