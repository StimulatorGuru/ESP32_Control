import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "Tens"

def write_control_frequency(freq: float):
    print(f"[WRITE] Setting frequency: {freq} Hz")
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("frequency", freq).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def write_control_enable(enabled: bool):
    val = 1 if enabled else 0
    print(f"[WRITE] Setting enable: {val}")
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("enable", val).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def read_latest_status():
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "settings")
      |> last()
    '''
    status = {"frequency": None, "totalPulseWidth": None, "enabled": None}
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        query_api = client.query_api()
        tables = query_api.query(query)
        for table in tables:
            for record in table.records:
                if record.get_field() == "frequency":
                    status["frequency"] = record.get_value()
                elif record.get_field() == "totalPulseWidth":
                    status["totalPulseWidth"] = record.get_value()
        return status

# Example usage:
# write_control_enable(True)
# write_control_frequency(50.0)
# print(read_latest_status())
