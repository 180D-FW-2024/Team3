from bluepy import btle
import struct
import time

SCALE_MAC_ADDRESS = "64:FB:01:1C:3E:82"
WEIGHT_MEASUREMENT_UUID = "f000ffc2-0451-4000-b000-000000000000"

class ScaleDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.weight_g = None  # Store the weight here

    def handleNotification(self, cHandle, data):
        """
        Callback for handling notifications from the scale.
        """
        try:
            if len(data) >= 10:
                # Extract bytes 8-9 (indices 8 and 9)
                weight_bytes = data[8:10]
                # Unpack as big-endian unsigned short
                self.weight_g = struct.unpack('>H', weight_bytes)[0]
        except Exception as e:
            print(f"Failed to parse data: {e}")

def get_weight_in_grams():
    device = None
    delegate = ScaleDelegate()
    try:
        print("Connecting to the scale...")

        # Attempt connection with a timeout of 20 seconds
        start_time = time.time()
        while True:
            try:
                device = btle.Peripheral(SCALE_MAC_ADDRESS)
                break  # Exit loop if connection is successful
            except btle.BTLEException:
                if time.time() - start_time > 20:
                    print("Failed to connect within 20 seconds.")
                    return None  # Return None if connection fails
                time.sleep(1)  # Wait before retrying

        device.setDelegate(delegate)
        print("Connected. Setting up notifications for weight measurement...")

        # Enable notifications for the Weight Measurement Characteristic
        weight_char = device.getCharacteristics(uuid=WEIGHT_MEASUREMENT_UUID)[0]
        descriptors = weight_char.getDescriptors(forUUID=0x2902)
        if not descriptors:
            raise ValueError("No Client Characteristic Configuration Descriptor (CCCD) found.")

        cccd = descriptors[0]
        device.writeCharacteristic(cccd.handle, b'\x01\x00')  # Enable notifications

        print("Waiting for weight measurement...")
        for _ in range(10):  # Try for a few seconds to get a notification
            if device.waitForNotifications(1.0):
                if delegate.weight_g is not None:
                    return delegate.weight_g  # Return the weight in grams
            print("No data yet, retrying...")
        
        print("Failed to get weight measurement within timeout.")
        return None  # Return None if no measurement is received

    except btle.BTLEException as e:
        print(f"Bluetooth error: {e}")
        return None  # Return None on Bluetooth error
    finally:
        if device:
            try:
                device.disconnect()
                print("Disconnected.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
