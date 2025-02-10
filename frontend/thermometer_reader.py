# from bluepy import btle
# import struct

# THERMOMETER_MAC_ADDRESS = "B8:1F:5E:37:BC:B8"
# TEMPERATURE_MEASUREMENT_UUID = "7edda774-045e-4bbf-909b-45d1991a2876"

# class ThermometerDelegate(btle.DefaultDelegate):
#     def __init__(self):
#         super().__init__()
#         self.current_temperature_f = None  # Store the latest temperature in Fahrenheit

#     def handleNotification(self, cHandle, data):
#         if cHandle != 31:
#             # Ignore notifications from other handles
#             return
        
#         try:
#             if len(data) == 8:
#                 # Unpack four 16-bit unsigned integers
#                 values = struct.unpack('<HHHH', data)
#                 temperature_raw = values[0]

#                 # Adjust the raw data to get Fahrenheit
#                 self.current_temperature_f = temperature_raw / 5.0
#             else:
#                 print("Unexpected data length for handle 31.")
                
#         except Exception as e:
#             print(f"Failed to parse data: {e}")

# def get_current_temperature_f():
#     """
#     Connects to the thermometer, reads the current temperature in Fahrenheit,
#     and returns the value.
#     """
#     device = None
#     delegate = ThermometerDelegate()
#     try:
#         # Connect to the thermometer
#         device = btle.Peripheral(THERMOMETER_MAC_ADDRESS)
#         device.setDelegate(delegate)

#         # Enable notifications for the Temperature Measurement Characteristic
#         temp_char = device.getCharacteristics(uuid=TEMPERATURE_MEASUREMENT_UUID)[0]
#         descriptors = temp_char.getDescriptors(forUUID=0x2902)
#         if not descriptors:
#             raise ValueError("No Client Characteristic Configuration Descriptor (CCCD) found.")
#         cccd = descriptors[0]
#         device.writeCharacteristic(cccd.handle, b'\x01\x00')  # Enable notifications

#         # Wait for a temperature reading
#         while delegate.current_temperature_f is None:
#             device.waitForNotifications(1.0)

#         # Return the current temperature in Fahrenheit
#         return delegate.current_temperature_f

#     except btle.BTLEException as e:
#         print(f"Bluetooth error: {e}")
#         return None
#     finally:
#         if device:
#             try:
#                 device.disconnect()
#             except Exception as e:
#                 print(f"Error during disconnect: {e}")


# -------------------------------------------------------------------------------------------
# API VERSION - TEMPORARY REPLACEMENT
import requests

import dotenv
import os

dotenv.load_dotenv()
MEATER_PASS = os.getenv("MEATER_PASSWORD")


# API Base URL
API_URL = "https://public-api.cloud.meater.com/v1"

# Your MEATER Cloud credentials
EMAIL = "abrandofhuangs@gmail.com"  # Replace with your MEATER Cloud email
PASSWORD = MEATER_PASS       # Replace with your MEATER Cloud password

def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def get_auth_token():
    """Authenticate and retrieve a JWT token."""
    url = f"{API_URL}/login"
    payload = {"email": EMAIL, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise error for bad status codes
    token = response.json()["data"]["token"]
    return token

def get_current_temperature_f():
    """Get the current temperature from the MEATER device."""
    token=get_auth_token()
    url = f"{API_URL}/devices"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    devices = response.json().get("data", {}).get("devices", [])
    if not devices:
        return "No devices found or connected."

    # Assuming the first device is the one you're monitoring
    device = devices[0]
    internal_temp = device["temperature"]["internal"]
    ambient_temp = device["temperature"]["ambient"]

    return celsius_to_fahrenheit(internal_temp)

if __name__ == "__main__":
    try:
        temperature_data = round(get_current_temperature_f())
        print("Current Temperature (F):", temperature_data)
    except requests.exceptions.RequestException as e:
        print("Error:", e)
