import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from influxdb_client import InfluxDBClient

# InfluxDB Cloud Settings
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "Tens"

def write_control_frequency(freq):
    url = f"{INFLUX_URL}/api/v2/write"
    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }
    params = {
        "org": ORG,
        "bucket": BUCKET,
        "precision": "s"
    }
    timestamp = int(time.time())
    data = f"control frequency={freq} {timestamp}"
    response = requests.post(url, headers=headers, params=params, data=data)
    print(f"[WRITE FREQ] {response.status_code}: {response.text.strip()}")

def write_control_enable(enabled):
    url = f"{INFLUX_URL}/api/v2/write"
    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }
    params = {
        "org": ORG,
        "bucket": BUCKET,
        "precision": "s"
    }
    value = 1 if enabled else 0
    timestamp = int(time.time())
    data = f"control enable={value} {timestamp}"
    response = requests.post(url, headers=headers, params=params, data=data)
    print(f"[WRITE ENABLE] {response.status_code}: {response.text.strip()}")

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
        df = pd.concat(tables, ignore_index=True) if isinstance(tables, list) else tables

    if df.empty:
        print("[READ] No data found.")
    else:
        df["_time"] = pd.to_datetime(df["_time"])
        df = df.set_index("_time")
    return df

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

# Set frequency and enable/disable
write_control_frequency(freq=30.0)
write_control_enable(enabled=True)  # True to enable, False to disable

time.sleep(5)

df = read_settings_data(minutes=5)
visualize_settings_data(df)
