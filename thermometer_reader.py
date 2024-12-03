from bluepy import btle
import struct
import time

THERMOMETER_MAC_ADDRESS = "B8:1F:5E:37:BC:B8"
TEMPERATURE_MEASUREMENT_UUID = "7edda774-045e-4bbf-909b-45d1991a2876"

class ThermometerDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.prev_temperature = None

    def handleNotification(self, cHandle, data):
        if cHandle != 31:
            # Ignore notifications from other handles
            return
        
        try:
            # Check if data length is as expected
            # print(f"Raw data in hex: {data.hex()}")
            if len(data) == 8:
                # Unpack four 16-bit unsigned integers
                values = struct.unpack('<HHHH', data)
                temperature_raw = values[0]

                # Adjust the raw data
                temperature_f = temperature_raw / 5.0

                # Convert to Celsius
                temperature_c = (temperature_f - 32) * 5.0 / 9.0

                # Round the temperature to one decimal place
                temperature_c = round(temperature_c, 1)

                # Check if temperature has changed
                if self.prev_temperature != temperature_c:
                    self.prev_temperature = temperature_c
                    print(f"Temperature changed: {temperature_f:.1f}°F ({temperature_c:.1f}°C)")
                else:
                    # Temperature hasn't changed; do not display output
                    pass
            else:
                print("Unexpected data length for handle 31.")
                
        except Exception as e:
            print(f"Failed to parse data: {e}")
            

def main():
    device = None  # Initialize device to None
    try:
        print("Connecting to the thermometer...")
        device = btle.Peripheral(THERMOMETER_MAC_ADDRESS)
        device.setDelegate(ThermometerDelegate())
        print("Connected. Setting up notifications for temperature measurement...")

        # Enable notifications for the Temperature Measurement Characteristic
        temp_char = device.getCharacteristics(uuid=TEMPERATURE_MEASUREMENT_UUID)[0]
        descriptors = temp_char.getDescriptors(forUUID=0x2902)
        
        if not descriptors:
            print("No Client Characteristic Configuration Descriptor (CCCD) found.")
            return
        else:
            cccd = descriptors[0]
            device.writeCharacteristic(cccd.handle, b'\x01\x00')  # Enable notifications
            print("Notifications enabled for temperature measurement.")

        print("Listening for temperature measurements... Press Ctrl+C to exit.")

        while True:
            if device.waitForNotifications(5.0):
                # Notification handled in callback
                continue
            # No notification received within timeout
            print("Waiting for data...")
            
    except btle.BTLEException as e:
        print(f"Bluetooth error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupt received. Exiting...")
    finally:
        if device:
            try:
                device.disconnect()
                print("Disconnected.")
            except Exception as e:
                print(f"Error during disconnect: {e}")

if __name__ == "__main__":
    main()
