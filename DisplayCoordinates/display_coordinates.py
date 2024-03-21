import json
import gmplot

with open("data.json", "r") as file:
    data = json.load(file)

first_device_data = list(data.values())[0]
first_position = first_device_data[0]["decrypted_payload"]
gmap = gmplot.GoogleMapPlotter(first_position["lat"], first_position["lon"], 13)
for device_id, positions in data.items():
    for pos in positions:
        lat = pos["decrypted_payload"]["lat"]
        lon = pos["decrypted_payload"]["lon"]
        gmap.marker(lat, lon, color='red')

gmap.draw("map.html")

print("Map generated! Open 'map.html' in a web browser to view.")
