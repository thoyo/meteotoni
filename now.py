from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import time

INFLUX_PORT = 8086
INFLUX_DATABASE = "meteotoni"
INFLUX_HOST = "influxdb_mt"
INFLUXDBCLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)

current_time = datetime.utcnow()
end_time = current_time + timedelta(days=365)
day_interval = timedelta(days=1)

while current_time < end_time:
    timestamps = [current_time + timedelta(minutes=i) for i in range(0, 24 * 60)]
    data_points = [
        {
            "measurement": "ones",
            "tags": {},
            "time": timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {"value": 100}
        } for timestamp in timestamps
    ]

    INFLUXDBCLIENT.write_points(data_points)

    time.sleep(1)  # Sleep for 1 second between batches
    current_time += day_interval

INFLUXDBCLIENT.close()

