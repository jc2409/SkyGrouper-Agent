import os
import json
import time
from datetime import date
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from apify_client import ApifyClient

def airbnb_scraper(location: str, checkin_date: str, checkout_date: str, num_adults: int, priceMax: int) -> Optional[Dict[str, Any]]:
    """
    Searches for available Airbnb listings in specified locations for given travel dates and number of guests.
    
    Args:
        location: List of location queries to scrape. E.g. London, Manchester, Birmingham, etc.
        checkin_date: check-in date for the airbnb. Visual format only allows YYYY-MM-DD
        checkout_date: check-out date for the airbnb. Visual format only allows YYYY-MM-DD
        num_adults: number of guests
        priceMax: Maximum price of the airbnb
        
    Returns:
        Optional[Dict[str, Any]]: A JSON-compatible dictionary containing Airbnb listings and metadata (e.g. prices, locations, availability) if the request is successful. Returns None if the request fails or yields no results.
    """
    try:
        load_dotenv()
        token = os.environ.get("AIRBNB_API_KEY")
        client = ApifyClient(token)
        
        run_input = {
            "locationQueries": [
                location
            ],
            "checkIn": checkin_date,
            "checkOut": checkout_date,
            "currency": "GBP",
            "adults": num_adults,
            "priceMax": priceMax
        }

        run = client.actor("NDa1latMI7JHJzSYU").start(run_input=run_input, wait_for_finish=8)
        run_id = run["id"]
        dataset_id = run.get("defaultDatasetId")

        client.run(run_id).abort()

        items = [] 
        if dataset_id:
            items = client.dataset(dataset_id).list_items().items
        return items
    
    except Exception as e:
        print("airbnb_scraper failed with:", e)

if __name__ == "__main__":
    dataset_items = airbnb_scraper("London", "2025-07-01", "2025-07-06", 4, 600)
    print(dataset_items)