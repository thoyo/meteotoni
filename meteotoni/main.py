from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import logging
from influxdb import InfluxDBClient
import time
import re
import json

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Starting program")

INFLUX_PORT = 8086
INFLUX_DATABASE = "meteotoni"
if os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False):
    INFLUX_HOST = "influxdb_mt"
else:
    INFLUX_HOST = "0.0.0.0"

INFLUXDBCLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)
SECONDS_IN_DAY = 3600 * 24
METEOCAT_DATE_FORMAT = "%Y-%m-%dZ"
METEOCAT_DATE_HOUR_FORMAT = "%Y-%m-%dT%H:%MZ"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
PATTERN = r"([a-zA-Z_]+_f)_(\d+)"

load_dotenv()
api_key = os.getenv("API_KEY")
BARCELONA_CODE = "080193"
if os.getenv("TEST") == "True":
    BASE_URL = "http://simulator:5000/pronostic/v1/municipal"
else:
    BASE_URL = "https://api.meteo.cat/pronostic/v1/municipal"


def get_data_daily(now):
    response = requests.get(f"{BASE_URL}/{BARCELONA_CODE}", headers={"Content-Type": "application/json", "X-Api-Key": api_key})

    formatted_date = datetime(now.year, now.month, 1, 0, 0, 0).strftime(DATETIME_FORMAT)
    query = f"SELECT response_status_code FROM \"meteocat_api\" WHERE time >= '{formatted_date}'"
    queries_this_month = len(list(INFLUXDBCLIENT.query(query).get_points()))

    point_out = {
        "measurement": "meteocat_api",
        "fields": {"response_status_code": response.status_code,
                   "queries_this_month": queries_this_month},
        "time": now.strftime(DATETIME_FORMAT)
    }
    ret = INFLUXDBCLIENT.write_points([point_out])
    if not ret:
        logging.error(f"Failed to write point to Influx: {json.dumps(point_out, indent=4)}")
    else:
        logging.info(f"Wrote point to Influx: {json.dumps(point_out, indent=4)}")

    if not response.ok:
        raise Exception(f"API returned {response.status_code} status code")

    return response.json()


def process_data_daily(data, now):
    logging.info(f"Got data {json.dumps(data, indent=4)}")
    for day in data["dies"]:
        points = []
        logging.info(f"Processing day {day['data']}")
        forecast_date = datetime.strptime(day["data"], METEOCAT_DATE_FORMAT)

        forecast_age_days = (forecast_date - datetime(now.year, now.month, now.day)).days

        formatted_date = forecast_date.strftime(DATETIME_FORMAT)

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
            },
            "time": formatted_date,
        }

        # # Gather existing forecast for same day and append to latest obtained ones,
        # to prevent overwriting existing with latest
        query = f"SELECT * FROM \"forecast\" WHERE time = '{formatted_date}'"
        result_data = list(INFLUXDBCLIENT.query(query).get_points())
        if len(result_data) > 1:
            raise Exception(f"Got unexpected number of items from Influx: {len(result_data)}")
        if len(result_data) == 1:
            for field in result_data[0]:
                if result_data[0][field] is None:
                    continue
                if field in ["time", "estat_cel", "precipitacio_f", "tmin_f", "tmax_f"]:
                    continue
                point_out["fields"][field] = result_data[0][field]
                if forecast_age_days == 0 and field[:9] != "estat_cel" and "err" not in field:
                    match = re.search(PATTERN, field)
                    age = match.group(2)
                    if int(age) == 0:
                        continue
                    point_out["fields"][f"{field}_err"] = (point_out["fields"][field] -
                                                           point_out["fields"][f"{match.group(1)}_0"])

        points.append(point_out)
        ret = INFLUXDBCLIENT.write_points(points)
        if not ret:
            logging.error(f"Failed to write points to Influx: {json.dumps(points, indent=4)}")
        else:
            logging.info(f"Wrote points to Influx: {json.dumps(points, indent=4)}")


def get_data_hourly(now):
    response = requests.get(f"{BASE_URL}Horaria/{BARCELONA_CODE}", headers={"Content-Type": "application/json", "X-Api-Key": api_key})

    formatted_date = datetime(now.year, now.month, 1, 0, 0, 0).strftime(DATETIME_FORMAT)
    query = f"SELECT response_status_code FROM \"meteocat_api\" WHERE time >= '{formatted_date}'"
    queries_this_month = len(list(INFLUXDBCLIENT.query(query).get_points()))

    point_out = {
        "measurement": "meteocat_api",
        "fields": {"response_status_code": response.status_code,
                   "queries_this_month": queries_this_month},
        "time": now.strftime(DATETIME_FORMAT)
    }
    ret = INFLUXDBCLIENT.write_points([point_out])
    if not ret:
        logging.error(f"Failed to write point to Influx: {json.dumps(point_out, indent=4)}")
    else:
        logging.info(f"Wrote point to Influx: {json.dumps(point_out, indent=4)}")

    if not response.ok:
        raise Exception(f"API returned {response.status_code} status code")

    return response.json()


def process_data_hourly(data):
    logging.info(f"Got data {json.dumps(data, indent=4)}")
    for day in data["dies"]:
        points = []
        for variable in ["estatCel", "precipitacio", "temp", "tempXafogor", "velVent", "dirVent", "humitat"]:
            values = day["variables"][variable].get("valors")
            if values is None:
                # Handle inconsistencies in response, sometimes encoding under valor, others valors
                values = day["variables"][variable].get("valor")
            for hour in values:
                logging.info(f"Processing hour {hour['data']}")
                forecast_date = datetime.strptime(hour["data"], METEOCAT_DATE_HOUR_FORMAT)
                formatted_date = forecast_date.strftime(DATETIME_FORMAT)

                point_out = {
                    "measurement": "forecast_hourly",
                    "fields": {variable: float(hour["valor"])},
                    "time": formatted_date,
                }

                points.append(point_out)
        ret = INFLUXDBCLIENT.write_points(points)
        if not ret:
            logging.error(f"Failed to write points to Influx: {json.dumps(points, indent=4)}")
        else:
            logging.info(f"Wrote points to Influx: {json.dumps(points, indent=4)}")


def main():
    now = datetime.now()

    data_hourly = get_data_hourly(now)
    process_data_hourly(data_hourly)

    data_daily = get_data_daily(now)
    process_data_daily(data_daily, now)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e, exc_info=True)
        time.sleep(SECONDS_IN_DAY)
