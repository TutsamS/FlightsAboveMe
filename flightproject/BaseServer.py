"""
@author: tutsamsingh
"""

import flightsbackend
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    
    def serve_image(self):
        # Path to the image file in the same directory as BaseServer.py
        image_path = os.path.join(os.path.dirname(__file__), "pm4.png")
        
        # Check if the image exists
        if os.path.exists(image_path):
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            
            # Read the image file in binary mode and write it to the response
            with open(image_path, "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Image not found", "utf-8"))
            
            
    def get_Marker_Script(self, suf, lat, lng, label, origin_country, altitude, icao24, velocity, heading, depart_airport, arrive_airport):
        infoContent = ""
        if label:
            infoContent = infoContent + "CallSign: <b>" + label + "</b><br>"
        if origin_country:
            infoContent = infoContent + "Country: <b>" + origin_country + "</b><br>"
        if altitude:
            infoContent = infoContent + "Altitude: <b>" + str(altitude) + " meters </b><br>"
        if icao24:
            infoContent = infoContent + "ICAO24: <b>" + str(icao24) + "</b><br>"
        if velocity:
            infoContent = infoContent + "Velocity: <b>" + str(velocity) + "</b><br>"
        if heading:
            infoContent = infoContent + "Heading: <b>" + str(heading) + "</b><br>"
        if depart_airport:
            infoContent = infoContent + "Departure: <b>" + str(depart_airport) + "</b><br>"
        if arrive_airport:
            infoContent = infoContent + "Arrival: <b>" + str(arrive_airport) + "</b><br>"
        sc = 'var marker' + str(suf) + ' = new google.maps.Marker({position: {lat: ' + str(lat) + ', lng: ' + str(lng) + '},map: map, label: "' + label + '", icon: "/pm4.png"});'
        sc = sc + "var infoWindow" + str(suf) + " = new google.maps.InfoWindow({content: '" + infoContent + "' });"
        sc = sc + "marker"+ str(suf) + ".addListener('mouseover', function() {infoWindow"+ str(suf) + ".open(map, marker"+ str(suf) + ");setTimeout(function() {document.querySelector('.gm-ui-hover-effect').style.display = 'none';}, 10);});"
        sc = sc + "marker"+ str(suf) + ".addListener('mouseout', function() {infoWindow"+ str(suf) + ".close();});"
        return sc
    
    def do_GET(self):
        if self.path == "/pm4.png":
            self.serve_image()
        else:
            city_name = urllib.parse.unquote(self.path)[1:]
            try:
                city_location = flightsbackend.get_city_location(city_name)
                flights = flightsbackend.get_flights_over_city(city_location)
                buttonClickScript = 'function redirectToLocation() { var location = document.getElementById("locationInput").value; if (location) {window.location.href = "/" + location;}}'
                myscrpt = 'function initMap() {'
                myscrpt = myscrpt + "var map = new google.maps.Map(document.getElementById('map'), {zoom: 10,center: {lat: " + str(city_location.latitude) + ", lng: " + str(city_location.longitude) + "}});"
                
                if flights:
                    counter = 1
                    for flight in flights:
                        print(f"Flight {flight['callsign']} (ICAO24: {flight['icao24']}) from {flight['origin_country']} at [{flight['latitude']}, {flight['longitude']}] at altitude {flight['altitude']} meters.")
                        myscrpt = myscrpt + self.get_Marker_Script(counter, flight['latitude'], 
                                                                   flight['longitude'], 
                                                                   flight['callsign'], 
                                                                   flight['origin_country'], 
                                                                   flight['altitude'], 
                                                                   flight['icao24'],
                                                                   flight['velocity'],
                                                                   flight['heading'],
                                                                   flight['departure_airport'],
                                                                   flight['arrival_airport'])
                        counter = counter + 1
                myscrpt = myscrpt + '}'
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>The Flight Project</title>", "utf-8"))
                #self.wfile.write(bytes('<script src="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"></script>', "utf-8"))
                self.wfile.write(bytes('<script>' +myscrpt + buttonClickScript + '</script>', "utf-8"))
                self.wfile.write(bytes("<style>html, body {height: 100%;margin: 0;padding: 0;overflow: hidden;} #map {height: 100%;width: 100%;position: fixed;top: 0;left: 0;z-index: 0;z-index: 0;}", "utf-8"))
                self.wfile.write(bytes(".top-center-form {position: absolute;top: 20px;left: 50%;transform: translateX(-50%);background: rgba(255, 255, 255, 0.8);padding: 10px;border-radius: 8px;box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.3);z-index: 1;} .gm-ui-hover-effect {display: none;}</style>", "utf-8"))
                self.wfile.write(bytes("</head>", "utf-8"))
                self.wfile.write(bytes('<body onload="initMap()">', "utf-8"))
                self.wfile.write(bytes('<div id="map"></div>', "utf-8"))
                self.wfile.write(bytes('<div class="top-center-form"> <input type="text" id="locationInput" placeholder="Enter location" /><button onclick="redirectToLocation()">Go</button></div>', "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
            except Exception as e:
                #myscript2 = 
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>The Flight Project</title>", "utf-8"))
                self.wfile.write(bytes("</head>", "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<p>No flights found over " + city_name + "</p>", "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
    
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
    
    

