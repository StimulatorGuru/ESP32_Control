import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Cloud Settings
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "qnAf-nmTbQPvEijcvmaQPOIK1qduzw57-reWjnQR90A2mdlsXWaNPmZ6dkISYQHMqHxzfESMxlT9wx5xYsyIuQ=="
ORG = "fb5d2e4c3ef2040a"
BUCKET = "Tens"

def write_control_frequency(freq):
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("frequency", freq).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def write_control_enable(enabled):
    value = 1 if enabled else 0
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("control").field("enable", value).time(time.time_ns())
        write_api.write(bucket=BUCKET, org=ORG, record=point)

def read_latest_status():
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "settings")
      |> last()
    '''
    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG) as client:
        query_api = client.query_api()
        tables = query_api.query(query, org=ORG)
        status = {"frequency": 0, "totalPulseWidth": 0, "enabled": False}
        for table in tables:
            for record in table.records:
                if record.get_field() == "frequency":
                    status["frequency"] = record.get_value()
                elif record.get_field() == "totalPulseWidth":
                    status["totalPulseWidth"] = record.get_value()
                elif record.get_field() == "enable":
                    status["enabled"] = bool(record.get_value())
        return status
