import bluetooth

target_name = "V-iPhone"
target_address = None

connected = 0
nearby_devices = bluetooth.discover_devices()

for bluetooth_addr in nearby_devices:
	if target_name == bluetooth.lookup_name(bluetooth_addr):
		target_address = bluetooth_addr
		connected = 1
		break

if target_address is not None:
	print("Found target bluetooth device with address", target_address)
else:
	print("Could not find target bluetooth device")