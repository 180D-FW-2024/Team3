from bluepy import btle
import struct

SCALE_MAC_ADDRESS = "64:FB:01:1C:3E:82"
WEIGHT_MEASUREMENT_UUID = "f000ffc2-0451-4000-b000-000000000000"

class ScaleDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.prev_weight_g = None

    def handleNotification(self, cHandle, data):
        """
        Callback for handling notifications from the scale.
        """
        try:
            # print(f"Raw data: {data}")
            if len(data) >= 10:
                # Extract bytes 8-9 (indices 8 and 9)
                weight_bytes = data[8:10]
                # Unpack as big-endian unsigned short
                weight_g = struct.unpack('>H', weight_bytes)[0]
                # Check if weight has changed
                if weight_g != self.prev_weight_g:
                    print(f"Received weight: {weight_g} g ({weight_g / 1000:.2f} kg)")
                    self.prev_weight_g = weight_g  # Update previous weight
            else:
                print("Received data is too short to parse weight.")
                
        except Exception as e:
            print(f"Failed to parse data: {e}")

def main():
    device = None  # Initialize device to None
    try:
        print("Connecting to the scale...")
        device = btle.Peripheral(SCALE_MAC_ADDRESS)
        device.setDelegate(ScaleDelegate())
        print("Connected. Setting up notifications for temperature measurement...")

        # Enable notifications for the Weight Measurement Characteristic
        weight_char = device.getCharacteristics(uuid=WEIGHT_MEASUREMENT_UUID)[0]
        descriptors = weight_char.getDescriptors(forUUID=0x2902)
        if not descriptors:
            print("No Client Characteristic Configuration Descriptor (CCCD) found.")
            return

        cccd = descriptors[0]
        device.writeCharacteristic(cccd.handle, b'\x01\x00')  # Enable notifications

        print("Listening for weight measurements... Press Ctrl+C to exit.")

        while True:
            if device.waitForNotifications(1.0):
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