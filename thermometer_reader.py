from bluepy import btle
import struct

THERMOMETER_MAC_ADDRESS = "B8:1F:5E:37:BC:B8"
TEMPERATURE_MEASUREMENT_UUID = "7edda774-045e-4bbf-909b-45d1991a2876"

class ThermometerDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.current_temperature_f = None  # Store the latest temperature in Fahrenheit

    def handleNotification(self, cHandle, data):
        if cHandle != 31:
            # Ignore notifications from other handles
            return
        
        try:
            if len(data) == 8:
                # Unpack four 16-bit unsigned integers
                values = struct.unpack('<HHHH', data)
                temperature_raw = values[0]

                # Adjust the raw data to get Fahrenheit
                self.current_temperature_f = temperature_raw / 5.0
            else:
                print("Unexpected data length for handle 31.")
                
        except Exception as e:
            print(f"Failed to parse data: {e}")

def get_current_temperature_f():
    """
    Connects to the thermometer, reads the current temperature in Fahrenheit,
    and returns the value.
    """
    device = None
    delegate = ThermometerDelegate()
    try:
        # Connect to the thermometer
        device = btle.Peripheral(THERMOMETER_MAC_ADDRESS)
        device.setDelegate(delegate)

        # Enable notifications for the Temperature Measurement Characteristic
        temp_char = device.getCharacteristics(uuid=TEMPERATURE_MEASUREMENT_UUID)[0]
        descriptors = temp_char.getDescriptors(forUUID=0x2902)
        if not descriptors:
            raise ValueError("No Client Characteristic Configuration Descriptor (CCCD) found.")
        cccd = descriptors[0]
        device.writeCharacteristic(cccd.handle, b'\x01\x00')  # Enable notifications

        # Wait for a temperature reading
        while delegate.current_temperature_f is None:
            device.waitForNotifications(1.0)

        # Return the current temperature in Fahrenheit
        return delegate.current_temperature_f

    except btle.BTLEException as e:
        print(f"Bluetooth error: {e}")
        return None
    finally:
        if device:
            try:
                device.disconnect()
            except Exception as e:
                print(f"Error during disconnect: {e}")

# Example usage
if __name__ == "__main__":
    temperature_f = get_current_temperature_f()
    if temperature_f is not None:
        print(f"Current Temperature: {temperature_f:.1f} °F")
    else:
        print("Failed to read temperature.")
