from flask import Flask, request, render_template, jsonify
from send_to_influx import write_control_frequency, write_control_enable, read_latest_status

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set", methods=["POST"])
def set_frequency():
    data = request.get_json()
    freq = data.get("freq")
    if freq is None:
        return jsonify({"message": "Frequency not provided."}), 400
    try:
        freq = float(freq)
        if 2 <= freq <= 150:
            write_control_frequency(freq)
            return jsonify({"message": f"Frequency set to {freq} Hz."}), 200
        else:
            return jsonify({"message": "Frequency out of range (2-150 Hz)."}), 400
    except ValueError:
        return jsonify({"message": "Invalid frequency value."}), 400

@app.route("/toggle", methods=["POST"])
def toggle_enable():
    data = request.get_json()
    enable = data.get("enable")
    if enable is None:
        return jsonify({"message": "Enable state not provided."}), 400
    try:
        write_control_enable(bool(enable))
        state = "enabled" if enable else "disabled"
        return jsonify({"message": f"Pulses {state}."}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/status")
def status():
    try:
        status = read_latest_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
