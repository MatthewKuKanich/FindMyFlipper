import base64

def gen(addr_hex, payload_hex):
    addr = bytearray.fromhex(addr_hex)
    key = bytearray(28)
    key[0:6] = addr[0:6]
    key[0] &= 0b00111111

    payload = bytearray.fromhex(payload_hex)
    key[6:28] = payload[7:29]
    key[0] |= (payload[29] << 6)

    return key

payload = input("enter payload: ").replace(" ", "")
mac = input("enter mac address: ").replace(" ", "").replace(":", "")
adv_key = bytes.fromhex(gen(mac.lower(), payload.lower()).hex())

with open(f"{mac}.keys", "w") as f:
    f.write(f"Advertisement key: {base64.b64encode(adv_key).decode('ascii')}")

print(f"Successfully generated key file: {mac}.keys")
