from flask import Flask, render_template, redirect, request, url_for
from bluetooth.ble import DiscoveryService

# Need to install pybluez:
# sudo apt-get update
# sudo apt-get install python-pip python-dev ipython
# sudo apt-get install bluetooth libbluetooth-dev
# sudo pip install pybluez

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():
	connected = 0
	error = None
	target_addr = " "

	if request.method == 'POST':
		target_addr = request.form['ConnName']

		service = DiscoveryService()
		devices = service.discover(2)

		for bluetooth_addr, name in devices.items():
			if target_addr == bluetooth_addr:
				connected = 1
				return redirect(url_for('connect'))


		# for bluetooth_addr in nearby_devices:
		# 	if target_name == bluetooth.lookup_name(bluetooth_addr):
		# 		target_address = bluetooth_addr
		# 		connected = 1
		# 		return redirect(url_for('connect'))
		

	return render_template("bluetooth.html", connection=connected)

@app.route("/connected")
def connect():
	return "Connected"

if __name__ == "__main__":
	app.run(debug = True)


# service = DiscoveryService()
# devices = service.discover(2)

# for address, name in devices.items():
# 	print("name: {}, address: {}".format(name, address))

#This can detect the arduino