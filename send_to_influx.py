import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# === InfluxDB Cloud Configuration ===
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "Tens"

def write_control_frequency(freq: float):
    """Writes the frequency to the 'control' measurement"""
    print(f"[WRITE] Setting frequency to: {freq:.2f} Hz")
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("frequency", freq).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def write_control_enable(enabled: bool):
    """Writes the enable status to the 'control' measurement (1 or 0 as integer)"""
    val = 1 if enabled else 0
    print(f"[WRITE] Setting enable to: {val}")
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("enable", val).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def read_latest_status():
    """Reads the most recent settings and enable state from InfluxDB"""
    settings_query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "settings")
      |> last()
    '''
    enable_query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "control" and r._field == "enable")
      |> last()
    '''

    status = {
        "frequency": None,
        "totalPulseWidth": None,
        "enabled": None
    }

    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        query_api = client.query_api()

        # Get settings
        settings_tables = query_api.query(settings_query)
        for table in settings_tables:
            for record in table.records:
                if record.get_field() == "frequency":
                    status["frequency"] = record.get_value()
                elif record.get_field() == "totalPulseWidth":
                    status["totalPulseWidth"] = record.get_value()

        # Get enable status
        enable_tables = query_api.query(enable_query)
        for table in enable_tables:
            for record in table.records:
                status["enabled"] = bool(record.get_value())

    print(f"[READ] Latest status: {status}")
    return status

# === Example usage ===
# write_control_enable(True)
# write_control_frequency(60.0)
# print(read_latest_status())
