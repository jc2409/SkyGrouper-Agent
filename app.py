# app.py  (Flask entry-point)
import asyncio
from datetime import date
from flask import Flask, request, jsonify
from agent_helpers import ask_agent
import json

app = Flask(__name__)


REQUIRED_FIELDS = {
    "user": str,
    "departure_airport": str,
    "destination_city": str, 
    "start_date": str,
    "end_date": str,
    "budget": int
}

def _parse_iso(d: str) -> date:
    return date.fromisoformat(d)

def validate_payload(js: dict) -> dict:
    cleaned = {}

    missing = [k for k in REQUIRED_FIELDS if k not in js]
    if missing:
        raise KeyError(f"Missing fields: {', '.join(missing)}")

    for k, typ in REQUIRED_FIELDS.items():
        val = js[k]
        if not isinstance(val, typ):
            try:
                val = typ(val)
            except Exception:
                raise TypeError(f"'{k}' must be {typ.__name__}")
        cleaned[k] = val

    sd, ed = _parse_iso(cleaned["start_date"]), _parse_iso(cleaned["end_date"])
    if ed <= sd:
        raise ValueError("'end_date' must be after 'start_date'")

    cleaned["start_date"], cleaned["end_date"] = sd, ed
    return cleaned

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


@app.post("/plan-trip")
def plan_trip():
    try:
        payload = request.get_json(force=True, silent=False)
        data = validate_payload(payload)
    except Exception as exc:
        status = 400 if isinstance(exc, (KeyError, TypeError, ValueError)) else 500
        return jsonify(error=str(exc)), status

    prompt = build_prompt(data)
    answer_text = asyncio.run(ask_agent(prompt))

    try:
        answer_json = json.loads(answer_text)
    except json.JSONDecodeError as e:
        answer_json = {"raw": answer_text, "error": str(e)}
    return jsonify(response=answer_json), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
