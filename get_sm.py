import json
import requests
import datetime
from bs4 import BeautifulSoup as BS
url = 'https://www.smchealth.org/coronavirus'
r = requests.get(url)

soup = BS(r.text, features="html.parser")

ctable = soup.table
deaths = ctable.find_all("tr")[2].find_all("td")[1].text
confirmed = ctable.find_all("tr")[1].find_all("td")[1].text
total = ctable.find_all("tr")[3].find_all("td")[1].text

updated_at = soup.find_all("em")[0].text.split(u"\xa0")[1] +":00-08:00"

date_time_obj = datetime.datetime.strptime(updated_at, '%m/%d/%Y at %H:%M:%S%z')

print("San Mateo stats: Deaths: {}, Confirmed: {}, Total: {}".format(deaths, confirmed, total))



san_mateo_covid_19={"last_update": date_time_obj.isoformat(),
                    "deaths": int(deaths),
                    "confirmed": int(confirmed),
                    "total": int(total)}

print (json.dumps(san_mateo_covid_19))
