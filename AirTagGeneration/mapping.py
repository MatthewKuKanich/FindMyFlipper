import json
import pandas as pd
import folium
import datetime
from folium.plugins import AntPath
from cores.pypush_gsa_icloud import icloud_login_mobileme, generate_anisette_headers
import requests
import logging 
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
import os
from colorama import Fore 
from pystyle import Colors, Colorate
import sys
import time

print(Colorate.Horizontal(Colors.purple_to_blue, f"""

    __  ___               ______                           __            
   /  |/  /___ _____     / ____/__  ____  ___  _________ _/ /_____  _____
  / /|_/ / __ `/ __ \   / / __/ _ \/ __ \/ _ \/ ___/ __ `/ __/ __ \/ ___/
 / /  / / /_/ / /_/ /  / /_/ /  __/ / / /  __/ /  / /_/ / /_/ /_/ / /    
/_/  /_/\__,_/ .___/   \____/\___/_/ /_/\___/_/   \__,_/\__/\____/_/     
            /_/                                                          
"""))
message =  f"""\n\
{Fore.GREEN}Made by Matthew KuKanich and Luu\n\
"""

for char in message:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.01)

def decrypt(enc_data, algorithm_dkey, mode):
    decryptor = Cipher(algorithm_dkey, mode, default_backend()).decryptor()
    return decryptor.update(enc_data) + decryptor.finalize()

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

def decrypt_data(report, priv_key):
    data = base64.b64decode(report)
    priv = int.from_bytes(base64.b64decode(priv_key), byteorder="big")
    timestamp = int.from_bytes(data[0:4], byteorder="big") + 978307200
    eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5:62])
    shared_key = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).exchange(ec.ECDH(), eph_key)
    symmetric_key = sha256(shared_key + b'\x00\x00\x00\x01' + data[5:62])
    iv = symmetric_key[16:]
    decryption_key = symmetric_key[:16]
    ciper_txt = data[62:72]
    auth_tag = data[72:]

    clear_text = decrypt(ciper_txt, algorithms.AES(decryption_key), modes.GCM(iv, auth_tag))

    result = {}
    latitude = struct.unpack(">i", clear_text[0:4])[0] / 10000000.0
    longitude = struct.unpack(">i", clear_text[4:8])[0] / 10000000.0
    confidence = int.from_bytes(clear_text[8:9], byteorder="big")
    status = int.from_bytes(clear_text[9:10], byteorder="big")

    result['timestamp'] = timestamp
    result['isodatetime'] = datetime.datetime.fromtimestamp(timestamp).isoformat()
    result['lat'] = latitude
    result['lon'] = longitude
    result['confidence'] = confidence
    result['status'] = status

    return result

message =  f"""\n\
{Fore.YELLOW}Enter your Hashed Advertisement key: \n\
"""

for char in message:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.01)

adv_key = input("")

if (len(adv_key) == 44):
    print("good key size")
    message =  f"""\n\
    {Fore.GREEN}Hours to search back in time: \n\
    """

    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)

    hours = int(input(""))
    if not (1 <= hours <= 24):

        print('Invalid amount of hours, range: 1-24 hours')
    else:
        with open("keys/auth.json", "r") as f:
            j = json.load(f)
        unix_epoch = int(datetime.datetime.now().timestamp())
        start_date = unix_epoch - (60 * 60 * hours)
        data = {"search": [{"startDate": start_date * 1000, "endDate": unix_epoch * 1000, "ids": [adv_key.strip().replace(" ", "")]}]}

        r = requests.post("https://gateway.icloud.com/acsnservice/fetch",
                      auth=(j["dsid"], j["searchPartyToken"]),
                      headers=generate_anisette_headers(),
                      json=data)
        encrypted_data = json.loads(r.content.decode(encoding='utf-8'))
        with open("encrypted_data.json", "w") as e:
            json.dump(encrypted_data, e)
        with open("encrypted_data.json", "r") as e:
            d = json.load(e)
        message =  f"""\n\
        {Fore.YELLOW}Enter your private key: \n\
        """
        for char in message:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)
        priv_key = input("")
        payloads = [item['payload'] for item in encrypted_data['results']]
        decrypted_data = []
        for payload in payloads:
            decrypted_payload = decrypt_data(payload, priv_key)
            decrypted_data.append(decrypted_payload)
        with open('data.json', 'w') as d:
            json.dump(decrypted_data, d, indent=4)
        os.remove("encrypted_data.json")
        
else:
    print("incorrect key size, the key is 'Hashed adv key' in the .keys file")


# just converting seconds to a more readable format lol
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

with open("data.json", "r") as file:
    data = json.load(file)

# this is mostly unchanged from your code
sorted_data = []
for pos in data:
    sorted_data.append(pos)
sorted_data.sort(key=lambda x: x["timestamp"])

# instead of making a list we can use a dataframe to make it easier to work with
# pandas has a bit of a learning curve but it's worth it
df = pd.DataFrame(sorted_data)

df['datetime'] = pd.to_datetime(df['isodatetime'])
df['time_diff'] = df['datetime'].diff().dt.total_seconds()
average_time_diff = df['time_diff'][1:].mean()
time_diff_total = (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds()

# we use the function we created here
formatted_total_time = format_time(time_diff_total)
formatted_avg_time = format_time(average_time_diff)

start_timestamp = df.iloc[0]['datetime'].strftime('%Y-%m-%d %H:%M:%S')
end_timestamp = df.iloc[-1]['datetime'].strftime('%Y-%m-%d %H:%M:%S')

# sanity check before plotting
if not df.empty:
    map_center = [df.iloc[0]['lat'], df.iloc[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=13)

    # Plotting path, idk how I feel about the animation so might change
    latlon_pairs = list(zip(df['lat'], df['lon']))
    ant_path = AntPath(locations=latlon_pairs[:-1], dash_array=[10, 20], delay=1000, color='black', weight=5, pulse_color='black') #changed to black for aesthetics
    m.add_child(ant_path)

    # added thius to find last marker
    last_latlon = latlon_pairs[-1]
    for index, row in df.iterrows():
        folium.Marker([row['lat'], row['lon']], popup=f"Timestamp: {row['isodatetime']}", tooltip=f"Point {index+1}", opacity=0).add_to(m) # made all of them invisible using opacity=0
    #made last one visible so you can see last position and not get confused when you have huge amounts of data
    folium.Marker(last_latlon, popup=f"Last Timestamp: {df.iloc[-1]['isodatetime']}", tooltip=f"Last Point, {index+1}", icon=folium.Icon(color='red', icon='circle', prefix='fa')).add_to(m)


    # this is just some basic html to make a persistant title as
    # well as some useful(ish) info about the data points
    title_and_info_html = f'''
     <h3 align="center" style="font-size:20px; margin-top:10px;"><b>FindMy Flipper Location Mapper</b></h3>
     <div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: 150px; z-index:9999; font-size:14px; background-color: white; padding: 10px; border-radius: 10px; box-shadow: 0 0 5px rgba(0,0,0,0.5);">
     <b>Location Summary</b><br>
     Start: {start_timestamp}<br>
     End: {end_timestamp}<br>
     Total Time: {formatted_total_time}<br>
     Average Time Between Pings: {formatted_avg_time}<br>
     Created by Matthew KuKanich and luu176<br>
     </div>
     '''
    m.get_root().html.add_child(folium.Element(title_and_info_html))

    m.save('advanced_map.html')
    message =  f"""\n\
    {Fore.RED}map info generated! Open 'advanced_map.html' in a web browser to view.\n\
    """

    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)
else:
    print("No data available to plot.")
