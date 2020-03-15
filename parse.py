import pandas as pd
import datetime

def ca_data(dataframe):
    dataframe = dataframe.rename(columns={"Country/Region":"Country", "Province/State": "State"})
    us_data = dataframe.loc[dataframe["Country"] == "US"]
    ca_data = us_data.query('State.str.contains("CA")')
    return ca_data


confirmed_filename = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
deaths_filename = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"

d=datetime.date.today()
today = d.strftime("%-m/%d/%y")
confirmed = pd.read_csv(confirmed_filename, header=0)
deaths = pd.read_csv(deaths_filename, header=0)

ca_confirmed = ca_data(confirmed)
ca_deaths = ca_data(deaths)

print (ca_confirmed)

