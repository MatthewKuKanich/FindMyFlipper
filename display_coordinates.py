import json
import gmplot

# Read data from JSON file
with open("data.json", "r") as file:
    data = json.load(file)

# Get the first position data
first_device_data = list(data.values())[0]
first_position = first_device_data[0]["decrypted_payload"]

# Initialize map centered at the first position
gmap = gmplot.GoogleMapPlotter(first_position["lat"], first_position["lon"], 13)

# Plot markers for each device's position data
for device_id, positions in data.items():
    for pos in positions:
        lat = pos["decrypted_payload"]["lat"]
        lon = pos["decrypted_payload"]["lon"]
        gmap.marker(lat, lon, color='red')

# Save the map to an HTML file
gmap.draw("map.html")

print("Map generated! Open 'map.html' in a web browser to view.")
