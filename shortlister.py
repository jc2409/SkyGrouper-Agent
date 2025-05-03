import asyncio, json, os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing in environment")

SYSTEM_TMPL = """You are **Travel-Planner-AI**, an assistant helping a group
choose European destinations.

Task
• Produce a ranked list of 4 European cities/towns that have airports.

Rules
1. Cities must be in Europe and have an IATA airport code.
2. Score ↑ when a city matches many of the group's interests.
3. Return exactly 4 items, ranked by score (break ties alphabetically).
4. Reply ONLY with minified JSON matching:

{
"candidates":[
  {"city":"string","iata":"string","score":number,
   "matched":["string"]}
]}"""

class ShortlisterClient:
    def __init__(self, api_key: str = API_KEY, model: str = "gpt-4.1-2025-04-14"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def get_shortlist(self, group_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        user_block = json.dumps(group_profiles, separators=(',', ':'))
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_TMPL},
                {"role": "user",   "content": user_block}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        data = self._parse(resp.choices[0].message.content)
        return data

    @staticmethod
    def _parse(txt: str) -> Dict[str, Any]:
        data = json.loads(txt)           # will raise if not valid JSON
        if "candidates" not in data:
            raise ValueError("Missing 'candidates' key")
        if len(data["candidates"]) != 4:
            raise ValueError(
                f"Expected 4 candidates, "
                f"got {len(data['candidates'])}"
            )
        return data
    
class ShortlisterSync:
    def __init__(self, *a, **kw):
        self._inner = ShortlisterClient(*a, **kw)

    def get_shortlist(self, group_profiles):
        return asyncio.run(self._inner.get_shortlist(group_profiles))

if __name__ == "__main__":
    sample_group = [
        {"username":"Andrew","interests":["culture","mountain"]},
        {"username":"Taya","interests":["beach","party","nightlife"]},
    ]

    scl = ShortlisterClient()
    shortlist = asyncio.run(scl.get_shortlist(sample_group))
    print(json.dumps(shortlist, indent=2))
