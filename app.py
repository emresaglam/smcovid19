from flask import Flask, jsonify, render_template, redirect
import json
import requests
import requests_cache
import datetime
from pytz import timezone
from bs4 import BeautifulSoup as BS
import os

app = Flask(__name__)
requests_cache.install_cache(cache_name='smhealth_cache', backend='sqlite', expire_after=600)

def get_sc():
    import json
    import re
    baseurl = "https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx"
    r = requests.get(baseurl)
    sc = BS(r.text, features="html.parser")
    scripts = sc.find_all("script")
    p = re.compile("\{.*\}")
    # WTF is going on below? I'm glad you asked
    # the data that we are looking for is in a script tag as a JSON Object. To be exact the 24th script in the page
    # Since JSON objects start and end with {} that;;s what we search in the script, extract, loads to a dictionary
    scdata = json.loads(p.search(scripts[23].text).group(0))
    confirmed = int(scdata["Total_Confirmed_Cases"])
    deaths = int(scdata["Deaths"])
    total = int(confirmed)
    updated_at = datetime.datetime.fromtimestamp(
        int(scdata["Modified"].split("(")[1].split("}")[0].split(")")[0][:-3])).isoformat()
    santa_clara_covid_19 = {"last_update": updated_at,
                            "deaths": deaths,
                            "confirmed": confirmed,
                            "total": total}
    print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {} (Cached response: {})"
          .format(deaths, confirmed, total, r.from_cache))

    return santa_clara_covid_19

def get_sm():
    import re
    baseurl = "https://www.smchealth.org/coronavirus"
    r = requests.get(baseurl)

    soup = BS(r.text, features="html.parser")

    ctable = soup.table
    deaths = ctable.find_all("tr")[2].find_all("td")[1].text
    confirmed = ctable.find_all("tr")[1].find_all("td")[1].text
    total = int(confirmed) + int(deaths)
    updated_as = soup.find_all("em")[0].text
    p = re.compile("\d\d/\d\d/\d\d\d\d at \d\d:\d\d")
    updated_at = p.search(updated_as).group(0)
    date_time_obj = datetime.datetime.strptime(updated_at, '%m/%d/%Y at %H:%M')

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

def get_sf():
    baseurl = "https://www.sfdph.org/dph/alerts/coronavirus.asp"
    r = requests.get(baseurl)
    sm = BS(r.text, features="html.parser")
    sm.find_all("div", {"class": "box2"})
    confirmed = int(sm.find_all("div", {"class", "box2"})[0].find_all("p")[0].text.split(":")[1])
    deaths = int(sm.find_all("div", {"class", "box2"})[0].find_all("p")[1].text.split(":")[1])
    if datetime.datetime.now(tz=timezone("US/Pacific")).hour < 10:
        yesterday = datetime.datetime.now(tz=timezone("US/Pacific")) - datetime.timedelta(days=1)
        updated_at = yesterday.replace(hour=10, minute=0,second=0,microsecond=0).isoformat()
    else:
        updated_at = datetime.datetime.now(tz=timezone("US/Pacific")).replace(hour=10, minute=0,second=0,microsecond=0).isoformat()
    total = deaths+confirmed

    san_francisco_covid_19 = {"last_update": updated_at,
                              "deaths": deaths,
                              "confirmed": confirmed,
                              "total": total}
    print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {} (Cached response: {})"
          .format(deaths, confirmed, total, r.from_cache))
    return san_francisco_covid_19

@app.route('/')
def api_root():
    sm_data = get_sm()

    return render_template("index.html", total = sm_data["total"], deaths = sm_data["deaths"]
                           , confirmed = sm_data["confirmed"])
        #"Oh hai! This is an API endpoint and this is not the URL you're looking for :)"


@app.route("/sm", methods=['GET'])
def sm():
    try:
        sm_data = get_sm()
    except ValueError:
        print("oops! We had a parsing error for SM")
        return render_template("500.html"), 500
    return jsonify(sm_data)

@app.route("/sf", methods=['GET'])
def sf():
    try:
        sf_data = get_sf()
    except ValueError:
        print("oops! We had a parsing error for SF")
        return render_template("500.html"), 500
    return jsonify(sf_data)

@app.route("/sc", methods=['GET'])
def sc():
    url="https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/dashboard.aspx"
    return redirect(url, code=302)


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
