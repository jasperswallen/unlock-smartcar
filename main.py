import smartcar
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)

# global variable to save our access_token
access = None
loggedin = False

client = smartcar.AuthClient(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    redirect_uri=os.environ.get('REDIRECT_URI'),
    scope=['read_vehicle_info','control_security'],
    test_mode=True
)


@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    global loggedin
    loggedin = True
    return redirect(auth_url)


@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')
    global loggedin

    if not loggedin:
        return 'Sorry, access denied. Please log in first', 401
    
    # access our global variable and store our access tokens
    global access
    # in a production app you'll want to store this in some kind of
    # persistent storage
    access = client.exchange_code(code)
    return 'got access codes', 200


@app.route('/vehicle', methods=['GET'])
def vehicle():
    # access our global variable to retrieve our access tokens
    global access
    global loggedin

    if not loggedin:
        return 'no vehicles', 400

    # the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    info = vehicle.info()
    print(info)

    return jsonify(info), 200

@app.route('/unlock', methods=['GET'])
def unlockCar():
    global access
    global loggedin
    
    if not loggedin:
        return 'no vehicles', 401

    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    vehicle.unlock()
    print('unlocked')

    return 'unlocked!', 200

@app.route('/logout', methods=['GET'])
def logout():
    global access
    global loggedin

    if not loggedin:
        print('no vehicles to disconnect')
        return 'no vehicles to disconnect', 200
    

    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    for vehicle_id in vehicle_ids:
        vehicle = smartcar.Vehicle(vehicle_id, access['access_token'])
        vehicle.disconnect()
        print('disconnected')

    loggedin = False

    return 'disconnected', 200


if __name__ == '__main__':
    app.run(port=8000)
