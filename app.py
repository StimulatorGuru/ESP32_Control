from flask import Flask, request, render_template
from send_to_influx import write_control_frequency, write_control_enable

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set", methods=["GET"])
def set_frequency():
    try:
        freq = float(request.args.get("freq"))
        if 2 <= freq <= 150:
            write_control_frequency(freq)
            return f"Frequency set to {freq} Hz", 200
        else:
            return "Frequency out of range (2-150 Hz)", 400
    except:
        return "Invalid frequency", 400

@app.route("/toggle", methods=["GET"])
def toggle_enable():
    try:
        enable = request.args.get("enable").lower() == "true"
        write_control_enable(enable)
        return f"Pulses {'enabled' if enable else 'disabled'}.", 200
    except:
        return "Invalid enable value", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
