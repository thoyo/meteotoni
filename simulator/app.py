from flask import Flask
import numpy as np
import datetime

METEOCAT_DATE_FORMAT = "%Y-%m-%dZ"

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {
        "dies": [
            {
                "data": datetime.datetime.now().strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=1)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=2)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=3)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=4)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=5)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
            {
                "data": (datetime.datetime.now()+datetime.timedelta(days=6)).strftime(METEOCAT_DATE_FORMAT),
                "variables": {
                    "estatCel": {"valor": 10},
                    "precipitacio": {"valor": np.random.uniform(0, 100)},
                    "tmin": {"valor": np.random.uniform(0, 15)},
                    "tmax": {"valor": np.random.uniform(15, 30)},
                },
            },
        ]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)