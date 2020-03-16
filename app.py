from flask import Flask, jsonify, render_template
import json
import requests
import requests_cache
import datetime
from bs4 import BeautifulSoup as BS
import os

app = Flask(__name__)
requests_cache.install_cache(cache_name='smhealth_cache', backend='sqlite', expire_after=600)

baseurl = "https://www.smchealth.org/coronavirus"


def get_sm():
    r = requests.get(baseurl)

    soup = BS(r.text, features="html.parser")

    ctable = soup.table
    deaths = ctable.find_all("tr")[2].find_all("td")[1].text
    confirmed = ctable.find_all("tr")[1].find_all("td")[1].text
    total = int(confirmed) + int(deaths)
    updated_at = soup.find_all("em")[0].text.split(u"\xa0")[1] + ":00-08:00"

    date_time_obj = datetime.datetime.strptime(updated_at, '%m/%d/%Y at %H:%M:%S%z')

    print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {} (Cached response: {})"
          .format(deaths, confirmed, total, r.from_cache))

    san_mateo_covid_19 = {"last_update": date_time_obj.isoformat(),
                          "deaths": int(deaths),
                          "confirmed": int(confirmed),
                          "total": total}

    san_mateo_covid_19_s = json.dumps(san_mateo_covid_19)
    response = san_mateo_covid_19
    print(san_mateo_covid_19_s)
    return response



@app.route('/')
def api_root():
    sm_data = get_sm()

    return render_template("index.html", total = sm_data["total"], deaths = sm_data["deaths"]
                           , confirmed = sm_data["confirmed"])
        #"Oh hai! This is an API endpoint and this is not the URL you're looking for :)"


@app.route("/sm", methods=['GET'])
def sm():
    sm_data = get_sm()
    return jsonify(sm_data)


if __name__ == '__main__':
    if os.environ.get('AIR_PORT'):
        port = os.environ.get('AIR_PORT')
    else:
        port = "5000"
    if os.environ.get('AIR_IP'):
        ip = os.environ.get('AIR_IP')
    else:
        ip = "127.0.0.1"
    if os.environ.get('DEBUG'):
        debug = True
    else:
        debug = False
    app.run(host=ip, debug=debug, port=port)
