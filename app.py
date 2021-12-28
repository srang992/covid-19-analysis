import streamlit as st
from functions import *

st.set_page_config(layout="wide")

st.title("Covid-19 Dashboard")

st.sidebar.title("Select the date and press 'Start'")

date = st.sidebar.date_input(label="Select Date")

is_clicked = st.sidebar.button("Start")

if is_clicked:
    total_confirmed_df, total_deaths_df, total_recovered_df = load_saved_data(date)
    total_confirmed, total_deaths, total_recovered, total_active = total_cases(total_confirmed_df,
                                                                               total_deaths_df, total_recovered_df)

    figure1 = covid_summary_for_a_specific_date(total_confirmed, total_deaths, total_recovered, total_active)

    figure2 = chloropleth_graph(total_confirmed_df)

    figure3, figure4 = SortByConfirmedAndDeathrate(total_confirmed_df, total_deaths_df)

    figure5 = DailyConfirmedCases()

    figure6 = DailyConfirmedCasesPer100k()

    st.plotly_chart(figure1, use_container_width=True)
    st.plotly_chart(figure2, use_container_width=True)
    st.plotly_chart(figure3, use_container_width=True)
    st.plotly_chart(figure4, use_container_width=True)
    st.plotly_chart(figure5, use_container_width=True)
    st.plotly_chart(figure6, use_container_width=True)
