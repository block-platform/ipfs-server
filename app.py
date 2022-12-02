import json
import requests

from flask_cors import CORS
from flask import Flask, request, jsonify, make_response

URL = "http://34.193.203.14:8080/ipfs-hash/%s"

PROJECTID = "2C3ti7yXc1nkKH6WNlNrrT13VKF"
PROJECTSECRET = "0e905e5ebd6c5aa010bb00fdb2ee8869"
INFURA_URL = "https://ipfs.infura.io:5001/api/v0/block/get"

app = Flask(__name__)
CORS(app)


def get_ipfs_hashes(email, password, device_id):
    url = URL % device_id
    response = requests.put(url, json={"email": email, "password": password})

    if response.status_code != 200:
        return None
    else:
        return response.json()


def get_ipfs_data(ipfs_hash):
    params = (("arg", ipfs_hash),)

    response = requests.post(INFURA_URL, params=params,
                             auth=(PROJECTID, PROJECTSECRET))

    response_json = response.text
    open_brace = response_json.find("{")
    close_brace = response_json.rfind("}")
    response_json = response_json[open_brace:close_brace+1]

    return json.loads(response_json)


@app.route("/iot/fetch-data/<device_id>", methods=["GET"])
def fetch_data(device_id):
    email = request.args.get("email")
    password = request.args.get("password")

    ipfs_hashes = get_ipfs_hashes(email, password, device_id)["ipfsHash"]

    if ipfs_hashes is None:
        return make_response(jsonify({"error": "Invalid credentials"}), 401)

    # Fetch data from IPFS
    data = []

    for ipfs_hash in ipfs_hashes:
        data.append(get_ipfs_data(ipfs_hash))

    return make_response(jsonify({"data": data}), 200)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
