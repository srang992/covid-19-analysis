import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup as soup
import datetime


def clean_and_load_data():
    """
     this function helps us to fetch the data from web and after that the data
     will be cleaned and saved in dataset folder.
    """

    base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
    confirmed_df = pd.read_csv(base_url + "time_series_covid19_confirmed_global.csv")
    deaths_df = pd.read_csv(base_url + "time_series_covid19_deaths_global.csv")
    recovered_df = pd.read_csv(base_url + "time_series_covid19_recovered_global.csv")

    # Data Preprocessing
    # -----------------------------------------------------------------------------------------------

    confirmed_df.drop(["Province/State", "Lat", "Long"], axis=1, inplace=True)
    deaths_df.drop(["Province/State", "Lat", "Long"], axis=1, inplace=True)
    recovered_df.drop(["Province/State", "Lat", "Long"], axis=1, inplace=True)

    confirmed_df = confirmed_df.groupby("Country/Region").aggregate(np.sum).T
    confirmed_df.index.name = "Date"
    confirmed_df = confirmed_df.reset_index()

    deaths_df = deaths_df.groupby("Country/Region").aggregate(np.sum).T
    deaths_df.index.name = "Date"
    deaths_df = deaths_df.reset_index()

    recovered_df = recovered_df.groupby("Country/Region").aggregate(np.sum).T
    recovered_df.index.name = "Date"
    recovered_df = recovered_df.reset_index()

    confirmed_df_melt = confirmed_df.melt(id_vars="Date")
    deaths_df_melt = deaths_df.melt(id_vars="Date")
    recovered_df_melt = recovered_df.melt(id_vars="Date")

    confirmed_df_melt.rename(columns={"value": "Confirmed"}, inplace=True)
    deaths_df_melt.rename(columns={"value": "Deaths"}, inplace=True)
    recovered_df_melt.rename(columns={"value": "Recovered"}, inplace=True)

    confirmed_df_melt['Date'] = pd.to_datetime(confirmed_df_melt['Date'])
    deaths_df_melt['Date'] = pd.to_datetime(deaths_df_melt['Date'])
    recovered_df_melt['Date'] = pd.to_datetime(recovered_df_melt['Date'])

    confirmed_df_melt['Date'] = confirmed_df_melt['Date'].dt.strftime("%Y/%m/%d")
    deaths_df_melt['Date'] = deaths_df_melt['Date'].dt.strftime("%Y/%m/%d")
    recovered_df_melt['Date'] = recovered_df_melt['Date'].dt.strftime("%Y/%m/%d")

    confirmed_df_melt.to_csv("datasets/covid_confirmed.csv", index=None)
    deaths_df_melt.to_csv("datasets/covid_deaths.csv", index=None)
    recovered_df_melt.to_csv("datasets/covid_recovered.csv", index=None)


def load_saved_data(date):
    """
     This function takes 2 arguments
    :param date: streamlit date input as a string.
    :return: total confirmed cases, total death cases, total recovered cases, total active cases.
    """
    date = date.strftime("%Y/%m/%d")

    confirmed_df_melt = pd.read_csv("datasets/covid_confirmed.csv")
    deaths_df_melt = pd.read_csv("datasets/covid_deaths.csv")
    recovered_df_melt = pd.read_csv("datasets/covid_recovered.csv")

    total_confirmed_df = confirmed_df_melt[confirmed_df_melt['Date'] == date]
    total_deaths_df = deaths_df_melt[confirmed_df_melt['Date'] == date]
    total_recovered_df = recovered_df_melt[confirmed_df_melt['Date'] == date]

    return total_confirmed_df, total_deaths_df, total_recovered_df


def total_cases(total_confirmed_df, total_deaths_df, total_recovered_df):
    total_confirmed = total_confirmed_df['Confirmed'].sum()
    total_deaths = total_deaths_df['Deaths'].sum()
    total_recovered = total_recovered_df['Recovered'].sum()
    total_active = total_confirmed - total_deaths - total_recovered

    return total_confirmed, total_deaths, total_recovered, total_active


def covid_summary_for_a_specific_date(total_confirmed, total_deaths, total_recovered, total_active):
    """
     this function takes 4 arguments:
    :param total_confirmed:
    :param total_deaths:
    :param total_recovered:
    :param total_active:
    :return: the required figure
    """
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode="number", value=int(total_confirmed),
                               number={'valueformat': 'f'},
                               title={'text': 'Total Confirmed Cases'},
                               domain={'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(mode='number', value=int(total_deaths),
                               number={'valueformat': 'f'},
                               title={'text': 'Total Death Cases'},
                               domain={'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(mode='number', value=int(total_recovered),
                               number={'valueformat': 'f'},
                               title={'text': 'Total Recovered Cases'},
                               domain={'row': 1, 'column': 0}))

    fig.add_trace(go.Indicator(mode='number', value=int(total_active),
                               number={'valueformat': 'f'},
                               title={'text': 'Total Active Cases'},
                               domain={'row': 1, 'column': 1}))

    fig.update_layout(grid={'rows': 2, 'columns': 2, 'pattern': 'independent'})

    return fig


def chloropleth_graph(total_confirmed_df):
    """
     Using this function we draw a chrolopleth graph using plotly. this takes one argument.
    :param total_confirmed_df: the main dataframe on which we are drawing the graph.
    :return: the desired figure.
    """
    pd.set_option('mode.chained_assignment', None)
    fig = px.choropleth(total_confirmed_df,
                        locations='Country/Region', locationmode='country names',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        color=np.log10(total_confirmed_df['Confirmed']),
                        range_color=(0, 10))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig


def SortByConfirmedAndDeathrate(total_confirmed_df, total_deaths_df):
    """
    Using this function we are going to see that which country is much more affected in Covid-19 if we sort the
    dataframe, first with respect to Confirmed cases and after that death rate in descending order respectively.

    :param total_confirmed_df: the dataframe containing the confirmed cases of all the countries.
    :param total_deaths_df: the dataframe containing the death cases of all the countries.
    :return: the required figure
    """
    A = total_confirmed_df.copy()
    A['Deaths'] = total_deaths_df['Deaths']
    A['DeathRate'] = (A['Deaths'] / A['Confirmed'] * 100).round(2)
    fig1 = px.scatter(A.sort_values('Confirmed', ascending=False).head(20),
                      x='Confirmed', y='Deaths', size='DeathRate', color='Country/Region')

    B = A.copy()
    B = B.sort_values('Deaths', ascending=False).head(20)

    fig2 = make_subplots(specs=[[{'secondary_y': True}]])
    fig2.add_trace(go.Bar(x=B['Country/Region'], y=B['Deaths'],
                          text=B['Deaths'], name='Deaths',
                          textposition='auto'), secondary_y=False)

    fig2.add_trace(go.Scatter(x=B['Country/Region'], y=B['DeathRate'],
                              text=B['DeathRate'], name='DeathRate (%)',
                              mode='markers+lines'), secondary_y=True)

    return fig1, fig2


def DailyConfirmedCases():
    """
    here we are going to see the daily confirmed cases across all countries.

    :return: the required figure.
    """
    confirmed_df_melt = pd.read_csv("datasets/covid_confirmed.csv")
    C = confirmed_df_melt.groupby('Date').aggregate(np.sum)
    C.index.name = 'Date'
    C['DailyConfirmed'] = C['Confirmed'].diff()
    C = C.reset_index()

    fig = px.area(C, x='Date', y='DailyConfirmed')

    return fig


def DailyConfirmedCasesPer100k():
    """
    here we are going to see the daily confirmed cases per 100k across all countries.

    :return: the required figure.
    """
    confirmed_df_melt = pd.read_csv("datasets/covid_confirmed.csv")
    # Retrieving the population data for all countries
    url = "https://www.worldometers.info/world-population/population-by-country/"
    r = requests.get(url)
    bs = soup(r.content, 'html')
    table = bs.find_all('table')[0]
    population_df = pd.read_html(str(table))[0]

    # Some basic preprocessing
    population_df.rename(columns={'Country (or dependency)': "Country/Region", "Population (2020)": "Population"},
                         inplace=True)
    population_df.drop(population_df.columns.difference(['Country/Region', 'Population']), axis=1, inplace=True)
    population_df.replace("United States", "US", inplace=True)

    # Daily confirmed cases per 100k across all countries for previous 2 weeks
    today = datetime.datetime.now()
    minus14 = today - datetime.timedelta(weeks=2)
    minus14 = minus14.strftime("%Y/%m/%d")
    D = confirmed_df_melt.copy()
    D = D[D['Date'] >= minus14]

    # Making the daily cases column
    D['Daily'] = D.groupby('Country/Region')['Confirmed'].diff()
    D.drop(['Date', 'Confirmed'], axis=1, inplace=True)
    D = D.groupby('Country/Region').sum()
    D = D.sort_values('Daily', ascending=False)

    # Making the per100k column after merging the population dataframe with the Dataframe D
    E = pd.merge(left=D, right=population_df, left_on='Country/Region', right_on='Country/Region')
    E['per100k'] = (E['Daily'] * 100000) / E['Population']
    fig = px.bar(E.sort_values('per100k', ascending=False).head(30).round(2),
                 x="Country/Region", y="per100k", text="per100k")

    return fig
