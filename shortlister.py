# shortlister.py
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_TMPL = """You are **Travel-Planner-AI**, an intelligent assistant helping a group of users choose European travel destinations.

Your task:
- Generate a ranked list of **10** European cities or towns with airports that best match the group’s combined interests.

Rules:
1. Suggest only cities or towns in **Europe** that are realistic travel destinations and have an associated IATA airport code.
2. Score each city by how well it matches the group's interests. A higher number of matched interests = higher score.
3. Include a **short justification** for each city to explain why it's a good match for the group.
4. Return exactly **10 results**, ranked by score (break ties alphabetically by city name).
5. Your reply must be a **valid, minified JSON** object following this schema:

{
  "candidates": [
    {
      "city": "string",
      "iata": "string",
      "score": number,
      "matched": ["string"],
      "justification": "string"
    }
  ]
}

Do not include any other keys, commentary, or formatting."""

load_dotenv()  # take environment variables from .env

api_key = os.getenv("api_key")
if api_key is None:
    raise ValueError("api_key not found in environment variables.")

class ShortlisterClient:
    def __init__(self, api_key: str, model: str = "gpt-4.1-2025-04-14"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def get_shortlist(self, 
                      group_profiles: List[Dict[str, Any]], 
                      k: int = 5) -> Dict[str, Any]:
        """Get generated destination suggestions for a group"""
        messages = self._build_messages(group_profiles, k)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,  # Allow creativity in generation
            response_format={"type": "json_object"}
        )

        return self._parse_response(response.choices[0].message.content)

    def _build_messages(self, 
                        group: List[Dict[str, Any]], 
                        k: int) -> List[Dict[str, str]]:
        """Construct the message array for OpenAI API"""
        user_block = (
            f"k = {k}\n\n"
            f"group = {json.dumps(group, separators=(',', ':'))}"
        )
        return [
            {"role": "system", "content": SYSTEM_TMPL},
            {"role": "user", "content": user_block}
        ]

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Validate and parse the API response"""
        try:
            data = json.loads(response_text)
            if "candidates" not in data:
                raise ValueError("Invalid response format: missing 'candidates'")
            return data
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON response")

# Sample group input (unchanged)
sample_group = [
    {"userId": "user1", "interests": ["culture", "mountain"]},
    {"userId": "user2", "interests": ["beach", "party", "nightlife", "live events"]},
    {"userId": "user3", "interests": ["sports"]},
    {"userId": "user4", "interests": ["culture", "live events", "party"]},
    {"userId": "user5", "interests": ["beach", "mountain", "sports", "culture", "nightlife"]},
    {"userId": "user6", "interests": ["nightlife", "party"]},
    {"userId": "user7", "interests": ["culture", "beach"]},
    {"userId": "user8", "interests": ["mountain"]},
    {"userId": "user9", "interests": ["live events", "sports", "party"]},
    {"userId": "user10", "interests": ["culture", "nightlife", "live events", "beach"]}
]


# Example usage
if __name__ == "__main__":
    client = ShortlisterClient(api_key)
    
    try:
        result = client.get_shortlist(
            group_profiles=sample_group,
            k=10
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
