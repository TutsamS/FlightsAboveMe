"""
@author: tutsamsingh
"""
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
from requests.auth import HTTPBasicAuth
import webbrowser
import time

def get_city_location(city_name):
    # Initialize geolocator
    geolocator = Nominatim(user_agent="bounding_box_app")
    
    # Get the location details for the city
    location = geolocator.geocode(str(city_name))
    if location is None:
        return f"City '{city_name}' not found."
    return location

def get_flight_details(icao24):
    current_time = int(time.time())
    begin_time = current_time - 3600 * 24  # Start time (24 hours ago)

    #INSERT OPENSKY API USERNAME AND PASSWORD BELOW AND UNCOMMENT
    #USERNAME = XXXXXXXXXXX
    #PASSWORD = XXXXXXXXXXX
    url = f"https://opensky-network.org/api/flights/aircraft?icao24={icao24}&begin={begin_time}&end={current_time}"
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response.raise_for_status()
        flights = response.json()
        
        if flights:
            latest_flight = flights[-1]  # Get the most recent flight
            return {
                "callsign": latest_flight['callsign'],
                "departure_airport": latest_flight['estDepartureAirport'],
                "arrival_airport": latest_flight['estArrivalAirport'],
                "departure_time": latest_flight['firstSeen'],
                "arrival_time": latest_flight['lastSeen'],
            }
        
        return "No recent flights found for this aircraft."
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def get_bounding_box(city_location, distance_km=10):
    
    # City latitude and longitude
    city_lat = city_location.latitude
    city_lon = city_location.longitude
    
    # Calculate the four corners of the bounding box by moving the distance in each direction
    # Move north (latitude increases)
    north_point = geodesic(kilometers=distance_km).destination((city_lat, city_lon), 0)
    # Move south (latitude decreases)
    south_point = geodesic(kilometers=distance_km).destination((city_lat, city_lon), 180)
    # Move east (longitude increases)
    east_point = geodesic(kilometers=distance_km).destination((city_lat, city_lon), 90)
    # Move west (longitude decreases)
    west_point = geodesic(kilometers=distance_km).destination((city_lat, city_lon), 270)
    
    
    # Define the bounding box
    bounding_box = {
        "latitude_min": south_point.latitude,
        "latitude_max": north_point.latitude,
        "longitude_min": west_point.longitude,
        "longitude_max": east_point.longitude
    }
    
    return bounding_box


def get_flights_in_area(latitude_min, latitude_max, longitude_min, longitude_max):
    #INSERT OPENSKY API USERNAME AND PASSWORD BELOW AND UNCOMMENT
    #USERNAME = XXXXXXXXXXXXXXXXXX
    #PASSWORD = XXXXXXXXXXXXXXXXXX

    url = "https://opensky-network.org/api/states/all"
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        
        if response.status_code == 200:
            data = response.json()
            flights = data.get('states', [])
            
            # Filter flights over the specified area (bounding box)
            flights_over_city = []
            for flight in flights:
                latitude = flight[6]
                longitude = flight[5]
                altitude = flight[7]
                
                if latitude and longitude: # and altitude:  # If altitude is 0 or NONE done display
                    if latitude_min <= latitude <= latitude_max and longitude_min <= longitude <= longitude_max:
                        icao24 = flight[0]
                        departure_airport = None
                        arrival_airport = None
                        try:
                            flight_details = get_flight_details(icao24)
                            departure_airport = flight_details['departure_airport']
                            arrival_airport = flight_details['arrival_airport']
                        except Exception as e:
                            print(f"Error fetching flight details for : {icao24}, {e}")
                            
                        flights_over_city.append({
                            'icao24': icao24,
                            'callsign': flight[1].strip(),
                            'origin_country': flight[2],
                            'longitude': flight[5],
                            'latitude': flight[6],
                            'altitude': flight[7],
                            'velocity': flight[9],
                            'heading': flight[10],
                            'departure_airport': departure_airport,
                            'arrival_airport': arrival_airport
                        })
            
            return flights_over_city if flights_over_city else None #"No flights found over the specified area."
        else:
            return f"Error fetching data: {response.status_code}"
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_flights_over_city(city_location):
    bb = get_bounding_box(city_location, distance_km=10)
    latitude_min = bb['latitude_min']
    latitude_max = bb['latitude_max']
    longitude_min = bb['longitude_min']
    longitude_max = bb['longitude_max']
    flights = get_flights_in_area(latitude_min, latitude_max, longitude_min, longitude_max)
    return flights
