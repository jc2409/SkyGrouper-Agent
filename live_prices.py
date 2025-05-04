import requests
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def get_coordinate(address: str):
    load_dotenv()
    outputFormat = "json"
    parameters = address
    api_key = os.environ.get("GOOGLE_MAPS")
    req = f"https://maps.googleapis.com/maps/api/geocode/{outputFormat}?{parameters}&key={api_key}"

def car_hire_live_prices(destinationPlace: str, pickupyear: int, pickupmonth: int, pickupday: int, dropoffyear: int, dropoffmonth: int, dropoffday: int) -> Optional[Dict[str, Any]]:
    """
    Initiates a car hire search session with the Skyscanner API to retrieve live car hire live prices.

    Args:
        destinationPlace: Place where the user is flying to
        pickupyear: pickup year of the car hire
        pickupmonth: pickup month of the car hire
        pickupday: pickup day of the car hire
        dropoffyear: dropoff year of the car hire
        dropoffmonth: dropoff month of the car hire
        dropoffday: dropoff day of the car hire
    
    Returns:
        Optional[Dict[str, Any]]: The JSON response from the API or None if the request fails
    """
    # API endpoint
    load_dotenv()
    api_key = os.environ.get("SKYSCANNER_API_KEY")
    url: str = "https://partners.api.skyscanner.net/apiservices/v1/carhire/live/search/create"

    # Headers
    headers: Dict[str, str] = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    # Request payload
    payload: Dict[str, Any] = {
        "query": {
            "market": "UK",
            "locale": "en-GB",
            "currency": "GBP",
            "pickUpDate": {
                
            },
            "adults": 1,
            "cabin_class": "CABIN_CLASS_ECONOMY"
        }
    }

    try:
        # Make the POST request
        response: requests.Response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        response.raise_for_status()
        results = response.json()
        # print(json.dumps(results, indent=4))
        return results

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")

    return None
def create_search_session(originPlace: str, destinationPlace: str, outboundYear: int, outboundMonth: int, outboundDay: int) -> Optional[Dict[str, Any]]:
    """
    Initiates a flight search session with the Skyscanner API to retrieve live ticket prices.

    Args:
        originPlace: Place where the user is flying from
        destinationPlace: Place where the user is flying to
        outboundYear: outbound year of the trip
        outboundMonth: outbound month of the trip
        outboundDay: outbound day of the trip
    
    Returns:
        Optional[Dict[str, Any]]: The JSON response from the API or None if the request fails
    """
    # API endpoint
    load_dotenv()
    api_key = os.environ.get("SKYSCANNER_API_KEY")
    url: str = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create"

    # Headers
    headers: Dict[str, str] = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    # Request payload
    payload: Dict[str, Any] = {
        "query": {
            "market": "UK",
            "locale": "en-GB",
            "currency": "GBP",
            "queryLegs": [
                {
                    "origin_place_id": {
                        "iata": originPlace
                    },
                    "destination_place_id": {
                        "iata": destinationPlace
                    },
                    "date": {
                        "year": outboundYear,
                        "month": outboundMonth,
                        "day": outboundDay
                    }
                    
                }
            ],
            "adults": 1,
            "cabin_class": "CABIN_CLASS_ECONOMY"
        }
    }

    try:
        # Make the POST request
        response: requests.Response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        response.raise_for_status()
        results = response.json()
        # print(json.dumps(results, indent=4))
        return results

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")

    return None