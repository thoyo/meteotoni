import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
if os.getenv("TEST") == "True":
    URL = "http://simulator:5000/referencia/v1/simbols"
else:
    URL = "https://api.meteo.cat/referencia/v1/simbols"
response = requests.get(URL, headers={"Content-Type": "application/json", "X-Api-Key": api_key})

out = "Value,Label\n"
for category in response.json():
    if category["nom"] == "cel":
        for symbol in category["valors"]:
            out += f"{symbol['codi']}, {symbol['nom']}\n"


with open("symbols.csv") as f:
    for line in f:
        line_split = line.split(",")
        print(f'                "{line_split[0]}"' + ": {")
        print(f'                  "index": {str(int(line_split[0])+1)}')
        print(f'                  "text": "{line_split[1]}"')
        print('                },')
