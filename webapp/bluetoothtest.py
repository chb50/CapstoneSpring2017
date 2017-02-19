from flask import Flask, render_template, redirect, request, url_for
import bluetooth

# Need to install pybluez:
# sudo apt-get update
# sudo apt-get install python-pip python-dev ipython
# sudo apt-get install bluetooth libbluetooth-dev
# sudo pip install pybluez

app = Flask(__name__)

#target_name = "V-iPhone" #This will connect to my iphone
target_address = None


@app.route("/", methods=['GET', 'POST'])
def main():
	connected = 0
	error = None
	target_name = " "

	if request.method == 'POST':
		target_name = request.form['ConnName']
		nearby_devices = bluetooth.discover_devices()

		for bluetooth_addr in nearby_devices:
			if target_name == bluetooth.lookup_name(bluetooth_addr):
				target_address = bluetooth_addr
				connected = 1
				return redirect(url_for('connect'))
		

	return render_template("bluetooth.html", connection=connected)

@app.route("/connected")
def connect():
	return "Connected"

if __name__ == "__main__":
	app.run(debug = True)

# PyBluez represents a bluetooth address as a string of the form ``xx:xx:xx:xx:xx", 
# where each x is a hexadecimal character representing one octet of the 48-bit address, 
# with most significant octets listed first. Bluetooth devices in PyBluez will always be 
# identified using an address string of this form.

# Choosing a device really means choosing a bluetooth address. If only the user-friendly name 
# of the target device is known, then two steps must be taken to find the correct address. 
# First, the program must scan for nearby Bluetooth devices. The routine discover_devices() 
# scans for approximately 10 seconds and returns a list of addresses of detected devices. 
# Next, the program uses the routine lookup_name() to connect to each detected device, 
# requests its user-friendly name, and compares the result to the target name.

# Since both the Bluetooth detection and name lookup process are probabilistic, 
# discover_devices() will sometimes fail to detect devices that are in range, and lookup_name() 
# will sometimes return None to indicate that it couldn't determine the user-friendly name 
# of the detected device. In these cases, it may be a good idea to try again once or twice 
# before giving up. 