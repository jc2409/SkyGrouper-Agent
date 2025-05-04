import requests
import json
import os
import argparse
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from live_prices import create_search_session
# from airbnb_scraper import airbnb_scraper

load_dotenv()

mcp = FastMCP("SweetSpot MCP Server")

@mcp.tool()
def search_live_prices(originPlace :str, destinationPlace :str, outboundYear :int, outboundMonth :int, outboundDay :int) -> Optional[Dict[str, Any]]:
    """
    Search for live flight prices using Skyscanner API.

    Args:
        originPlace: Place where the user is flying from
        destinationPlace: Place where the user is flying to
        outboundYear: outbound year of the trip
        outboundMonth: outbound month of the trip
        outboundDay: outbound day of the trip
    
    Returns:
        Optional[Dict[str, Any]]: The JSON response from the API or None if the request fails
    """
    response = create_search_session(originPlace, destinationPlace, outboundYear, outboundMonth, outboundDay)
    return response

# @mcp.tool()
# def scrape_airbnb(location: str, checkin_date: str, checkout_date: str, num_adults: int, priceMax: int) -> Optional[Dict[str, Any]]:
#     """
#     Searches for available Airbnb listings in specified locations for given travel dates and number of guests.

#     Args:
#         location: List of location queries to scrape. E.g. London, Manchester, Birmingham, etc.
#         checkin_date: check-in date for the airbnb. Visual format only allows YYYY-MM-DD
#         checkout_date: check-out date for the airbnb. Visual format only allows YYYY-MM-DD
#         num_adults: number of guests
#         priceMax: Maximum price of the airbnb
        
#     Returns:
#         Optional[Dict[str, Any]]: A JSON-compatible dictionary containing Airbnb listings and metadata (e.g. prices, locations, availability) if the request is successful. Returns None if the request fails or yields no results.
#     """   
#     airbnb_list = airbnb_scraper(location, checkin_date, checkout_date, num_adults, priceMax)
#     return airbnb_list
    
if __name__ == "__main__":
    mcp.run(transport="sse")