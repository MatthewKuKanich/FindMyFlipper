#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <ArduinoJson.h> // Json support for python script to read data easier


class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      const uint8_t* payload = advertisedDevice.getPayload();
      int payloadLength = advertisedDevice.getPayloadLength();
      if (payloadLength > 2 && payload[0] == 0x1E && payload[1] == 0xFF && payload[2] == 0x4C) {
          DynamicJsonDocument jsonDocument(256); // Create a JSON document
          jsonDocument["RSSI"] = advertisedDevice.getRSSI();
          String payloadData = "";
          for (int i = 0; i < payloadLength; i++) {
            char hex[3];
            sprintf(hex, "%02X", payload[i]);
            payloadData += hex;
          }
          jsonDocument["Payload_Data"] = payloadData;
          jsonDocument["MAC_Address"] = advertisedDevice.getAddress().toString().c_str();
          char buffer[256];
          serializeJson(jsonDocument, buffer);
          Serial.println(buffer); // Output the json data
      }
    }
};

void setup() {
  Serial.begin(115200);
  BLEDevice::init("");
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->start(0);
}

void loop() {
  
}