
import streamlit as st
from functions import *

st.set_page_config(layout="wide")

st.title("Covid-19 Dashboard")

st.write("To see the results, please open the side panel and press 'Start' :smile:. "
         "The rest will happen automatically.")

st.subheader("Results: ")

st.sidebar.title("Covid-19 Analysis")

st.sidebar.write("""
The analysis is done on JHU CSSE COVID-19 data. The data containing all the covid-19 details of all countries. 
Here I am taking 3 dataframe from github repository - the dataset for the confirmed cases, the death cases and the 
recovery cases. to see all the visualizations, first press the button 'Download', it will take some time. when 
this is done, press the 'Start' button.
""")

date = st.sidebar.date_input(label="Select Date")

st.sidebar.text('')
col1, col2 = st.sidebar.columns([1, 1])

is_downloaded = col1.button("Download")
is_clicked = col2.button("Start")

if is_downloaded:
    clean_and_load_data()
    st.sidebar.write("Data Downloaded and processed successfully")

if is_clicked:
    total_confirmed_df, total_deaths_df, total_recovered_df = load_saved_data(date)
    total_confirmed, total_deaths, total_recovered, total_active = total_cases(total_confirmed_df,
                                                                               total_deaths_df, total_recovered_df)

    figure1 = covid_summary_for_a_specific_date(total_confirmed, total_deaths, total_recovered, total_active)

    figure2 = chloropleth_graph(total_confirmed_df)

    figure3, figure4 = SortByConfirmedAndDeathrate(total_confirmed_df, total_deaths_df)

    figure5 = DailyConfirmedCases()

    figure6 = DailyConfirmedCasesPer100k()

    st.write("This Chart gives us a little summary on **Total Confirmed Cases**, **Total Death Cases**,"
             " **Total Recovery Cases** "
             "and **Total Active Cases** till now.")
    st.plotly_chart(figure1, use_container_width=True)

    st.write("This plot shows the **Chloropleth graph** of those countries in the dataset. Here the more dark colour "
             "denotes the low confirmed cases of that country and the less dark colour denotes the high confirmed "
             "cases of that country.")
    st.plotly_chart(figure2, use_container_width=True)

    st.write("This is the **Confirmed vs Deaths** Scatter plot in which the size of the circle is determined "
             "by the percentage of the death i.e. **Death Rate**.")
    st.plotly_chart(figure3, use_container_width=True)

    st.write("In this stacked graph I am drawing inference on **Top 20 countries which are highest in Deaths**. "
             "the bars denotes the **Death Count** and the line denotes the **Death Rate**")
    st.plotly_chart(figure4, use_container_width=True)

    st.write("In this graph, I am drawing inference on **Daily Confirmed Cases** across all the countries.")
    st.plotly_chart(figure5, use_container_width=True)

    st.write("In this graph, I am drawing inference on **Daily Confirmed Cases per 100k** across all the countries.")
    st.plotly_chart(figure6, use_container_width=True)
