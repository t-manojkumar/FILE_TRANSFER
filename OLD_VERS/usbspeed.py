import usb.core
import usb.util
import usb.backend.libusb1

# USB speed constants
USB_SPEEDS = {
    1: "Low Speed (1.5 Mbps)",
    2: "Full Speed (12 Mbps)",
    3: "High Speed (480 Mbps)",
    4: "SuperSpeed (5 Gbps)",
    5: "SuperSpeed+ (10 Gbps)"
}

def list_usb_devices():
    backend = usb.backend.libusb1.get_backend()
    devices = usb.core.find(find_all=True, backend=backend)
    if not devices:
        print("No USB devices found.")
        return

    for device in devices:
        speed = USB_SPEEDS.get(device.speed, f"Unknown Speed (Raw value: {device.speed})")
        print(f"Device: ID {hex(device.idVendor)}:{hex(device.idProduct)}")
        print(f"  Manufacturer: {usb.util.get_string(device, device.iManufacturer)}")
        print(f"  Product: {usb.util.get_string(device, device.iProduct)}")
        print(f"  Speed: {speed}")
        print("-" * 40)

if __name__ == "__main__":
    list_usb_devices()
