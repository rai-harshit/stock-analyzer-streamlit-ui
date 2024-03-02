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

LOGGER = get_logger(__name__)

DATABASE_URL = st.secrets["DATABASE_URL"]
TABLE_NAME_IRCTC = "irctc_stock_data"
TABLE_NAME_BSE = "bse_stock_data"

def fetch_data(table_name):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(f"SELECT * FROM {table_name} where date > '2019-07-31'", engine)
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
        comparisons between two tickers- Bombay Stock Exchange (BSE) and Indian Railway 
        Catering and Tourism Corporation (IRCTC).
        This tool does not contain any complex analysis. It is a simple frontend created
        while learning Airflow, an orchestration tool, that is used to run ETL pipelines in a
        scheduled manner.
    """
    )

    with st.spinner("Fetching latest data for you..."):
      df_irctc = fetch_data(TABLE_NAME_IRCTC)
      df_irctc["ticker"] = "IRCTC"
      df_bse = fetch_data(TABLE_NAME_BSE)
      df_bse["ticker"] = "BSE"

    combined_df = pd.concat([df_irctc, df_bse], ignore_index=True)

    combined_df["perct_change"] = (combined_df["open"] - combined_df["close"]) / combined_df["open"]

    chart = alt.Chart(combined_df[combined_df["ticker"]=="IRCTC"]).mark_line().encode(
    x='date',
    y='close',
    tooltip=['date', 'close'] 
    ).interactive()

    chart = chart.properties(title='IRCTC Growth since IPO')

    st.altair_chart(chart, use_container_width=True)
    
    chart = alt.Chart(combined_df).mark_line().encode(
    x='date',
    y='perct_change',
    color='ticker',
    tooltip=['date', 'perct_change', 'ticker'] 
    ).interactive()

    chart = chart.properties(title='IRCTC vs BSE- Daily Percentage Change')

    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    run()
