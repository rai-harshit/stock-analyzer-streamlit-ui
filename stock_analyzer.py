# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
from sqlalchemy import create_engine
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

LOGGER = get_logger(__name__)

DATABASE_URL = st.secrets["DATABASE_URL"]
TABLE_NAME = "stock_data"

def fetch_data(table_name, ticker):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(f"SELECT * FROM {table_name} where date > '2019-07-31' and ticker = '{ticker}'", engine)
    return df


def run():
    st.set_page_config(
        page_title="Stock Analyzer",
        page_icon="💰",
    )

    st.write("# Welcome to the Stock Analyzer! 👋")

    st.markdown(
        """
        The Stock Analyzer is a simple dashboard that contains some interesting trends and
        comparisons between two tickers- NIFTYBEES.BSE, LICI.BSE, and IRCTC.BSE.\n
        This tool does not contain any complex analysis. It is a simple frontend created
        while learning Airflow, an orchestration tool, that is used to run ETL pipelines in a
        scheduled manner.
    """
    )

    with st.spinner("Fetching latest data for you..."):
      df_irctc = fetch_data(TABLE_NAME, 'IRCTC.BSE')
      df_nifty = fetch_data(TABLE_NAME, 'NIFTYBEES.BSE')
      df_lic = fetch_data(TABLE_NAME, 'LICI.BSE')

    combined_df = pd.concat([df_irctc, df_nifty, df_lic], ignore_index=True)

    chart_irctc = alt.Chart(combined_df[combined_df["ticker"]=="IRCTC.BSE"]).mark_line().encode(
    x='date',
    y='close',
    tooltip=['date', 'close'] 
    ).interactive()

    chart_irctc = chart_irctc.properties(title='IRCTC since IPO')
    st.altair_chart(chart_irctc, use_container_width=True)

    chart_lic = alt.Chart(combined_df[combined_df["ticker"]=="LICI.BSE"]).mark_line().encode(
    x='date',
    y='close',
    tooltip=['date', 'close'] 
    ).interactive()

    chart_lic = chart_lic.properties(title='LIC since IPO')
    st.altair_chart(chart_lic, use_container_width=True)

    chart_nifty = alt.Chart(combined_df[combined_df["ticker"]=="NIFTYBEES.BSE"]).mark_line().encode(
    x='date',
    y='close',
    tooltip=['date', 'close'] 
    ).interactive()

    chart_nifty = chart_nifty.properties(title='NIFTYBEES since October 2019')
    st.altair_chart(chart_nifty, use_container_width=True)

    # Create a single chart with both lines
    combined_chart = alt.Chart(combined_df[combined_df["ticker"] != "NIFTYBEES.BSE"]).mark_line().encode(
        x='date',
        y='close',
        color='ticker:N'  # Use ticker as a color encoding to differentiate lines
    ).interactive()

    # Add customizations (optional)
    combined_chart = combined_chart.properties(
        title='IRCTC vs LIC Performance'  # Combined title
    ).configure_axis(
        labelFontSize=12,  # Adjust label font size
        titleFontSize=14  # Adjust title font size
    )

    # Display the combined chart
    st.altair_chart(combined_chart, use_container_width=True)
    
    chart = alt.Chart(combined_df).mark_line().encode(
    x='date',
    y='pct_change',
    color='ticker',
    tooltip=['date', 'pct_change', 'ticker'] 
    ).interactive()

    chart = chart.properties(title='IRCTC vs LIC vs NIFTY50BEES - Daily Percentage Change')

    st.altair_chart(chart, use_container_width=True)

    correlation_df = pd.DataFrame({
        'IRCTC': df_irctc['pct_change'],
        'LIC': df_lic['pct_change'],
        'NIFTY': df_nifty['pct_change']
    })

    # Calculate correlation matrix
    correlation_matrix = correlation_df.corr()
    st.set_option('deprecation.showPyplotGlobalUse', False)

    # Plot correlation matrix heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    st.pyplot()

    st.write("##### ETL Pipeline powered by Airflow")
    st.markdown(
        """
        The ETL (Extract-Transform-Load) pipeline fetches data from the Alpha Vantage API,
        converts the JSON response into CSV format, calculates delta between runs, adds
        derived field to the data, and then ingests the resulting data into the PostgreSQL
        database hosted on Aiven.io.\n
        This ETL pipeline used Apache Airflow to run once every day to bring in the latest 
        stock data from the API. The API sends all the historical data during each run. 
        The Delta stage ensures that we are processing and ingesting the entire historical 
        data every single time. This results in improved performance- both in terms of time 
        and space.
    """
    )
    st.image("img/etl-airflow.png")


if __name__ == "__main__":
    run()
