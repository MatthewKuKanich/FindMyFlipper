import serial
import json
import os
import msvcrt
import base64
import subprocess


command = "esptool --baud 921600 write_flash 0x1000 sniffer_bootloader.bin 0x8000 sniffer_partitions.bin 0x10000 airtag_sniffer.bin"
try:
    subprocess.run(command, shell=True)
    print("sniffer installed..")
    print("proceeding...")
except Exception as e:
    print(e)


def gen(addr_hex, payload_hex):
    addr = bytearray.fromhex(addr_hex)
    key = bytearray(28)
    key[0:6] = addr[0:6]
    key[0] &= 0b00111111

    payload = bytearray.fromhex(payload_hex)
    key[6:28] = payload[7:29]
    key[0] |= (payload[29] << 6)

    return key


os.system('cls')
def select_serial_port():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device}")
    selection = input("Select the port number: ")
    try:
        selection = int(selection)
        if 1 <= selection <= len(ports):
            return ports[selection - 1].device
        else:
            print("Invalid selection. Please choose a number from 1 to", len(ports))
            return select_serial_port()
    except ValueError:
        print("Invalid input. Please enter a number.")
        return select_serial_port()


esp32_port = select_serial_port()
airtags = []

ser = serial.Serial(esp32_port, 115200, timeout=1)

try:
    while True:
        data = ser.readline().strip().decode('utf-8')
        if msvcrt.kbhit():
                    key = msvcrt.getwche()
                    if key == '\r':  # Enter key
                        break
        if data:
            try:
                os.system('cls')
                json_data = json.loads(data)
                index_to_insert = 0
                try:
                    for i in range(len(airtags)):
                        if airtags[i]["RSSI"] < json_data["RSSI"]:
                            index_to_insert = i
                            break
                except:
                    index_to_insert = 0
                airtags.insert(index_to_insert, json_data)
                count = 0
                for item in airtags:
                    count += 1
                    rssi = item['RSSI']
                    payload = item['Payload_Data']
                    mac = item['MAC_Address']
                    print(f"{count}:")
                    print("RSSI:", rssi)
                    print("Payload data:", payload)
                    print("MAC:", mac, "\n")
                print("Press Enter if Airtag found")
                
                
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

except KeyboardInterrupt:
    print("KeyboardInterrupt: Exiting...")
finally:
    ser.close()
choice = input("Which Number?: ")
try: 
    print("Selected Airtag:", airtags[(int(choice))-1]["MAC_Address"])
    actual_payload = (airtags[(int(choice))-1]["Payload_Data"]).replace(" ", "")
    actual_mac = (airtags[(int(choice))-1]["MAC_Address"]).replace(" ", "").replace(":", "")
    adv_key = bytes.fromhex(gen(actual_mac.lower(), actual_payload.lower()).hex())

    with open(f"{actual_mac}.keys", "w") as f:
        f.write(f"Advertisement key: {base64.b64encode(adv_key).decode('ascii')}")

    print(f"Successfully generated flipper file: {actual_mac}.keys")

except Exception as e:
    print("Incorrect value", e)
