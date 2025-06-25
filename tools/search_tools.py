import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain_core.tools import tool

load_dotenv()

@tool
def search_travel_info(query: str) -> str:
    """
    Search the web for travel-related information using Google Search.
    
    This tool can help find information about:
    - Hotel reviews and ratings
    - Flight prices and schedules
    - Tourist attractions and activities
    - Travel tips and recommendations
    - Restaurant reviews
    - Local events and weather
    
    Args:
        query: The search query to look up travel information
        
    Returns:
        str: Formatted search results with titles and links, or error message
    """
    try:
        # Check if API key is available
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY not found in environment variables."
        
        # Perform the search
        search = GoogleSearch({
            "q": query,
            "api_key": api_key,
            "num": 5,  
            "gl": "us",  
            "hl": "en"  
        })
        
        data = search.get_dict()
        
        # Handle potential API errors
        if "error" in data:
            return f"Search API error: {data['error']}"
        
        # Extract organic results
        results = data.get("organic_results", [])
        
        if not results:
            return "No search results found for your query."
        
        # Format results with titles, snippets, and links
        formatted_results = []
        for i, result in enumerate(results[:5], 1):
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "")
            
            # Create formatted result entry
            result_entry = f"{i}. **{title}**\n   {snippet}\n   🔗 {link}"
            formatted_results.append(result_entry)
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error performing search: {str(e)}"

@tool 
def search_hotels(location: str, checkin: str = "", checkout: str = "", guests: str = "2") -> str:
    """
    Search for hotels in a specific location with optional dates and guest count.
    
    Args:
        location: The city or area to search for hotels
        checkin: Check-in date (optional, format: YYYY-MM-DD)
        checkout: Check-out date (optional, format: YYYY-MM-DD) 
        guests: Number of guests (optional, default: 2)
        
    Returns:
        str: Hotel search results with names, ratings, and booking links
    """
    try:
        # Build search query
        query = f"hotels in {location}"
        if checkin and checkout:
            query += f" {checkin} to {checkout}"
        if guests != "2":
            query += f" for {guests} guests"
        
        # Use the main search function
        return search_travel_info(query)
        
    except Exception as e:
        return f"Error searching hotels: {str(e)}"

@tool
def search_flights(origin: str, destination: str, date: str = "", passengers: str = "1") -> str:
    """
    Search for flights between two locations with optional date and passenger count.
    
    Args:
        origin: Departure city or airport
        destination: Arrival city or airport
        date: Travel date (optional, format: YYYY-MM-DD)
        passengers: Number of passengers (optional, default: 1)
        
    Returns:
        str: Flight search results with airlines, prices, and booking information
    """
    try:
        # Build search query
        query = f"flights from {origin} to {destination}"
        if date:
            query += f" on {date}"
        if passengers != "1":
            query += f" for {passengers} passengers"
        
        # Use the main search function
        return search_travel_info(query)
        
    except Exception as e:
        return f"Error searching flights: {str(e)}"

search_tool = search_travel_info
hotel_search_tool = search_hotels
flight_search_tool = search_flights