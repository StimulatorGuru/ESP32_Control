from flask import Flask, request, render_template
from send_to_influx import write_control_frequency

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
