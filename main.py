from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import logging
from influxdb import InfluxDBClient
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Starting program")

INFLUX_PORT = 8086
INFLUX_DATABASE = "meteotoni"
URL = "https://api.meteo.cat/pronostic/v1/municipal/080193"
if os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False):
    INFLUX_HOST = "influxdb_mt"
else:
    INFLUX_HOST = "0.0.0.0"

INFLUXDBCLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)
SECONDS_IN_DAY = 3600 * 24
METEOCAT_DATE_FORMAT = "%Y-%m-%dZ"

load_dotenv()
api_key = os.getenv("API_KEY")


def get_data(now):
    response = requests.get(URL, headers={"Content-Type": "application/json", "X-Api-Key": api_key})

    point_out = {
        "measurement": "meteocat_api",
        "fields": {"response_status_code": response.status_code},
        "time": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    ret = INFLUXDBCLIENT.write_points([point_out])
    if not ret:
        logging.error(f"Failed to write point to Influx: {point_out}")
    else:
        logging.info(f"Wrote point to Influx: {point_out}")

    if not response.ok:
        raise Exception(f"API returned {response.status_code} status code")

    return response.json()


def process(data, now):
    logging.info(f"Got data {data}")
    points = []
    for day in data["dies"]:
        forecast_date = datetime.strptime(day["data"], METEOCAT_DATE_FORMAT)

        time_difference = forecast_date - datetime(now.year, now.month, now.day)
        forecast_age_days = time_difference.days

        formatted_date = forecast_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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

        # Gather existing forecast for same day and append to latest obtained ones,
        # to prevent overwriting existing with latest
        query = f"SELECT * FROM \"forecast\" WHERE time = '{formatted_date}'"
        result_data = INFLUXDBCLIENT.query(query)
        for result in result_data:
            for field in result:
                if field == "time":
                    continue
                point_out["fields"][field] = result[field]

        points.append(point_out)
        ret = INFLUXDBCLIENT.write_points(points)
        if not ret:
            logging.error(f"Failed to write points to Influx: {points}")
        else:
            logging.info(f"Wrote points to Influx: {points}")


def main():
    now = datetime.now()

    data = get_data(now)
    process(data, now)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e)
        time.sleep(SECONDS_IN_DAY)
