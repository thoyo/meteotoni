from datetime import datetime
import requests
import pprint as pp
from dotenv import load_dotenv
import os
import logging
from influxdb import InfluxDBClient
import time

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
logging.info("Starting program")

INFLUX_PORT = 8086
INFLUX_DATABASE = "meteotoni"
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    INFLUX_HOST = "influxdb"
else:
    INFLUX_HOST = "0.0.0.0"

INFLUXDBCLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)

load_dotenv()

# Replace TOKEN with your own Telegram API token
key = os.getenv("API_KEY")

while True:
    url = "https://api.meteo.cat/pronostic/v1/municipal/080193"
    response = requests.get(url, headers={"Content-Type": "application/json", "X-Api-Key": key})
    data = response.json()
    points = []
    for day in data["dies"]:
        # Parse the date string into a datetime object
        date = datetime.strptime(day["data"], '%Y-%m-%dZ')

        # Format the datetime object as required for InfluxDB
        formatted_date = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        point_out = {
            "measurement": "forecast",
            "fields": {
                "estat_cel": day["variables"]["estatCel"]["valor"],
                "precipitacio": day["variables"]["precipitacio"]["valor"],
                "tmin": day["variable"]["tmin"]["valor"],
                "tmax": day["variable"]["tmax"]["valor"],
            },
            "time": formatted_date
        }
        points.append(point_out)
        ret = INFLUXDBCLIENT.write_points(points)
    pp.pprint(response.json())
    time.sleep(3600)

