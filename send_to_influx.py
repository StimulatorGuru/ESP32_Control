import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from influxdb_client import InfluxDBClient, Point, Dialect

# --- InfluxDB Cloud Settings ---
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "IOT_control"

# === 1. Function: Write Control Frequency ===
def write_control_frequency(freq):
    url = f"{INFLUX_URL}/api/v2/write"
    params = {
        "org": ORG,
        "bucket": BUCKET,
        "precision": "s"
    }

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    timestamp = int(time.time())
    data = f"control frequency={freq} {timestamp}"

    response = requests.post(url, params=params, headers=headers, data=data)
    print(f"[WRITE] Status: {response.status_code}, Message: {response.text.strip()}")

# === 2. Function: Read Settings (frequency, duty cycle, pulse width) ===
def read_settings_data(minutes=5):
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -{minutes}m)
      |> filter(fn: (r) => r._measurement == "settings")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "frequency", "dutyCycle", "totalPulseWidth"])
    '''

    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        tables = client.query_api().query_data_frame(query)
        if isinstance(tables, list) and len(tables) > 0:
            df = pd.concat(tables, ignore_index=True)
        else:
            df = tables

    if df.empty:
        print("[READ] No data found.")
    else:
        df["_time"] = pd.to_datetime(df["_time"])
        df = df.set_index("_time")
    return df

# === 3. Function: Visualize Data ===
def visualize_settings_data(df):
    if df.empty:
        print("No data to plot.")
        return

    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(df.index, df["frequency"], label="Frequency (Hz)", color='blue')
    plt.ylabel("Frequency (Hz)")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(df.index, df["dutyCycle"], label="Duty Cycle (%)", color='green')
    plt.ylabel("Duty Cycle (%)")
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(df.index, df["totalPulseWidth"], label="Total Pulse Width (µs)", color='red')
    plt.ylabel("Pulse Width (µs)")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

# === USAGE ===

# Step 1: Write control frequency (optional)
write_control_frequency(freq=25.0)  # Change frequency as needed

# Step 2: Wait for ESP32 to read and respond
time.sleep(10)

# Step 3: Read and visualize settings
df = read_settings_data(minutes=5)
visualize_settings_data(df)
