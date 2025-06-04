import time
import requests
import pandas as pd
from influxdb_client import InfluxDBClient

# ==== InfluxDB Cloud Configuration ====
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "Tens"

# ==== Helper: Write to InfluxDB ====
def _write_line_protocol(measurement: str, field: str, value, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())

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
    data = f"{measurement} {field}={value} {timestamp}"
    response = requests.post(url, headers=headers, params=params, data=data)

    print(f"[WRITE] {measurement}.{field} = {value} | {response.status_code}: {response.text.strip()}")
    if response.status_code >= 300:
        raise RuntimeError(f"Failed to write data: {response.text.strip()}")

# ==== Write Control Functions ====
def write_control_frequency(freq: float):
    _write_line_protocol("control", "frequency", freq)

def write_control_enable(enabled: bool):
    value = 1 if enabled else 0
    _write_line_protocol("control", "enable", value)

# ==== Read Recent Settings for Visualization ====
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

# ==== Read Latest Values for UI (/status API) ====
def read_latest_status():
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "settings")
      |> filter(fn: (r) => r._field =~ /frequency|totalPulseWidth|enable/)
      |> last()
    '''

    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        result = client.query_api().query(org=ORG, query=query)

    status = {
        "frequency": 0,
        "totalPulseWidth": 0,
        "enabled": False
    }

    for table in result:
        for record in table.records:
            field = record.get_field()
            value = record.get_value()

            if field == "frequency":
                status["frequency"] = round(float(value), 2)
            elif field == "totalPulseWidth":
                status["totalPulseWidth"] = round(float(value), 2)
            elif field == "enable":
                status["enabled"] = bool(value)

    return status

# ==== Optional: Plot Settings Data (for local use) ====
def visualize_settings_data(df):
    if df.empty:
        print("No data to plot.")
        return

    import matplotlib.pyplot as plt

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

# ==== Example usage (optional standalone testing) ====
if __name__ == "__main__":
    write_control_frequency(50.0)
    write_control_enable(True)

    time.sleep(2)

    df = read_settings_data()
    visualize_settings_data(df)

    print("Latest status:", read_latest_status())
