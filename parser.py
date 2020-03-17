import requests
import requests_cache
from bs4 import BeautifulSoup as BS
import datetime
from pytz import timezone

class CountyParser:
    def __init__(self):
        requests_cache.install_cache(cache_name='smhealth_cache', backend='sqlite', expire_after=600)

    def get_sm(self):
        baseurl = "https://www.smchealth.org/coronavirus"
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

    def get_sf(self):
        baseurl = "https://www.sfdph.org/dph/alerts/coronavirus.asp"
        r = requests.get(baseurl)
        sm = BS(r.text, features="html.parser")
        sm.find_all("div", {"class": "box2"})
        confirmed = int(sm.find_all("div", {"class", "box2"})[0].find_all("p")[0].text.split(":")[1])
        deaths = int(sm.find_all("div", {"class", "box2"})[0].find_all("p")[1].text.split(":")[1])
        if datetime.datetime.now(tz=timezone("US/Pacific")).hour < 10:
            yesterday = datetime.datetime.now(tz=timezone("US/Pacific")) - datetime.timedelta(days=1)
            updated_at = yesterday.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
        else:
            updated_at = datetime.datetime.now(tz=timezone("US/Pacific")).replace(hour=10, minute=0, second=0,
                                                                                  microsecond=0).isoformat()
        total = deaths + confirmed

        san_francisco_covid_19 = {"last_update": updated_at,
                                  "deaths": deaths,
                                  "confirmed": confirmed,
                                  "total": total}
        print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {} (Cached response: {})"
              .format(deaths, confirmed, total, r.from_cache))
        return san_francisco_covid_19

    def get_sc(self):
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
        confirmed = scdata["Total_Confirmed_Cases"]
        deaths = scdata["Deaths"]
        total = confirmed
        updated_at = datetime.datetime.fromtimestamp(int(scdata["Modified"].split("(")[1].split("}")[0].split(")")[0][:-3])).isoformat()
        santa_clara_covid_19 = {"last_update": updated_at,
                                  "deaths": deaths,
                                  "confirmed": confirmed,
                                  "total": total}
        print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {} (Cached response: {})"
              .format(deaths, confirmed, total, r.from_cache))

        return santa_clara_covid_19