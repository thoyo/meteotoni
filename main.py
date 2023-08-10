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

key = os.getenv("API_KEY")

while True:
    url = "https://api.meteo.cat/pronostic/v1/municipal/080193"
    response = requests.get(url, headers={"Content-Type": "application/json", "X-Api-Key": key})
    data = response.json()
    points = []
    for day in data["dies"]:
        # Parse the date string into a datetime object
        date = datetime.strptime(day["data"], '%Y-%m-%dZ')
        forecast_age_days = (date -
                             datetime.combine(datetime.now().date(), datetime.min.time())).total_seconds() / 3600 / 24
        # Format the datetime object as required for InfluxDB
        formatted_date = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        point_out = {
            "measurement": "forecast",
            "fields": {
                f"estat_cel_{forecast_age_days}": day["variables"]["estatCel"]["valor"],
                f"estat_cel": day["variables"]["estatCel"]["valor"],
                f"precipitacio_f_{forecast_age_days}": float(day["variables"]["precipitacio"]["valor"]),
                f"precipitacio_f": float(day["variables"]["precipitacio"]["valor"]),
                f"tmin_f_{forecast_age_days}": float(day["variables"]["tmin"]["valor"]),
                f"tmin_f": float(day["variables"]["tmin"]["valor"]),
                f"tmax_f_{forecast_age_days}": float(day["variables"]["tmax"]["valor"]),
                f"tmax_f": float(day["variables"]["tmax"]["valor"]),
                "forecast_age_days": forecast_age_days,
            },
            "time": formatted_date,
        }
        query = f'SELECT * FROM "forecast" WHERE time = \'{formatted_date}\''
        result_data = INFLUXDBCLIENT.query(query)
        for result in result_data:
            for field in result:
                if field == "time":
                    continue
                point_out["fields"][field] = result[field]

        points.append(point_out)
        ret = INFLUXDBCLIENT.write_points(points)
    pp.pprint(response.json())

    time.sleep(3600 * 12)
