import requests
import json
import os
import argparse
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from live_prices import *

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
    create_response =create_search_session(originPlace, destinationPlace, outboundYear, outboundMonth, outboundDay)
    return create_response

if __name__ == "__main__":
    mcp.run(transport="sse")