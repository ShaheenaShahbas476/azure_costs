
import streamlit as st
import pandas as pd
import psycopg2 as ps
from psycopg2 import Error
import pandas as pd
from datetime import datetime, timezone
from streamlit_navigation_bar import st_navbar
import os




st.set_page_config(page_title="Mindhappy Solutions", layout="wide")
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

def get_db_connection():
    global connection , cursor
    try:
        connection = ps.connect(host = "localhost",
            database = "postgres",
            user = "postgres",
            password = "postgres"
        )
        connection.autocommit = True
        cursor = connection.cursor()
        return connection , cursor
    
    except Error as e:
        st.error("Error connecting to the database.")
        st.error(e)
        return None, None

def fetch_data(query, params=None):
    try:
        conn, cur = get_db_connection()
        if not conn or not cur:
            return None
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error executing query: {query}")
        st.error(e)
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()



conn, cur = get_db_connection()

if conn and cur:
    styles = {
    "nav": {
        "background-color": "mediumpurple",
        "justify-content": "left",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "active": {
        "background-color": "white",
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "14px",
    }
    }

    page = st_navbar(["Home", "Azure"],logo_path= r"Frame001.svg",styles = styles)
    st.write(page)
    if page =="Home":

        column = st.columns([65,35])
        with column[0]:
            st.markdown(
        """
        
        <div >
        <p style="color:mediumpurple;font-size:50px"><b> Optimize your</b>
        <img src='aws.jpg' alt=" AWS |" style="vertical-align: middle;"><img src='azure.png' alt="Azure |" style="vertical-align: middle;"><img src='snowflake.png' alt="Snowflake" style="vertical-align: middle;"><span style="vertical-align: middle;"><b> Bill</b></span> 
          </p><br>
          
        <ul style="color: hotpink;">
        <li> Actionable Recommendations that will provide optimal Cost without degrading performance</li>
        <li>Recommendations usually requires minor config changes without major Quality checks    </li>
        <li>Recommendations for Committed usage - Savings Plan, Reserved Instances </li>
        <li>Detailed Cost Analysis Report that provides breakdown of top cost drivers and potential areas of concern</li>

        </ul>
        <br>
        <a href="https://calendar.app.google/nPvQFTJyREfytt7r6">
        <button style="background-color:mediumpurple;color:white;border:2px mediumpurple;font-size:18px;">Book for a Call</button>
        </a>

        </div>

        """,
        unsafe_allow_html=True)
         
            
        with column[1]:
                st.image('cloud.jpg')
 
    elif page == "Azure":

        tabs = st.tabs(["VM"])
        with tabs[0]:
        

            regions_query = "SELECT DISTINCT location FROM vm_pricing order by location"
            regions_data = fetch_data(regions_query)
            regions = [row[0] for row in regions_data] if regions_data else []

            cols = st.columns([1.5, 1, 1, 1, 1, 1, 1])
            with cols[0]:
                selected_region = st.selectbox(label="Regions", options=regions, label_visibility='visible')
            with cols[1]:
                selected_pricing = st.selectbox(label="Pricing Unit", options=["Instance", "vCPUs",  "Memory"], index=0, label_visibility='visible')
            with cols[2]:
                selected_cost = st.selectbox(label="Cost", options=["Per Second", "Per Minute", "Hourly", "Daily", "Weekly", "Monthly", "Annually"], index=2, label_visibility='visible')


        
        with st.container():
            cost_multiplier = {
                "Per Second": 1 / 3600,
                "Per Minute": 1 / 60,
                "Hourly": 1,
                "Daily": 24,
                "Weekly": 24 * 7,
                "Monthly": 24 * 30,
                "Annually": 24 * 365
            }

            multiplier = cost_multiplier[selected_cost]


            join_query = f"""
            SELECT 
                name AS Name,
                location as Location,
                instance_memory AS Instance_Memory,
                vcpus AS vCPUs,
                instance_storage AS Instance_Storage,

                linux_on_demand_cost * {multiplier} AS Linux_On_Demand_Cost,
                linux_savings_price_1_Year * {multiplier} AS Linux_Savings_Price_1_Year,
                linux_savings_price_3_Years * {multiplier} AS Linux_Savings_Price_3_Years,
                linux_reservation_1_year * {multiplier}  AS Linux_Reservation_1_Year,
                linux_reservation_3_years * {multiplier} AS Linux_Reservation_3_Years,
                linux_spot_cost * {multiplier}  AS Linux_Spot_Cost,
                windows_on_demand_cost * {multiplier}  AS Windows_On_Demand_Cost,
                windows_savings_price_1_year * {multiplier} AS Windows_Savings_Price_1_Year,
                windows_savings_price_3_years * {multiplier} AS Windows_Savings_Price_3_Years,
                windows_reservation_1_year * {multiplier}  AS Windows_Reservation_1_Year,
                windows_reservation_3_years * {multiplier} AS Windows_Reservation_3_Years,
                windows_spot_cost * {multiplier} AS Windows_Spot_Cost
            FROM 
                vm_pricing 
        WHERE location = '{selected_region}'
        
            ORDER BY 
            location ASC, name ASC;
            """

            joined_data = fetch_data(join_query)
            joined_columns = [
                "Name", "Location", "Instance Memory", "vCPUs", "Instance Storage",
                "Linux On Demand Cost", "Linux Savings Price 1 Year", "Linux Savings Price 3 Years",
                "Linux Reservation 1 Year", "Linux Reservation 3 Years", "Linux Spot Cost",
                "Windows On Demand Cost", "Windows Savings Price 1 Year", "Windows Savings Price 3 Years",
                "Windows Reservation 1 Year", "Windows Reservation 3 Years", "Windows Spot Cost"
            ]

            if joined_data:
                joined_df = pd.DataFrame(joined_data, columns=joined_columns)
                

                if selected_pricing == "vCPUs":
                    for cost_col in [
                        "Linux On Demand Cost", "Linux Spot Cost", "Windows On Demand Cost", 
                        "Windows Spot Cost", "Linux Savings Price 1 Year", "Linux Savings Price 3 Years",
                        "Linux Reservation 1 Year", "Linux Reservation 3 Years",
                        "Windows Savings Price 1 Year", "Windows Savings Price 3 Years",
                        "Windows Reservation 1 Year", "Windows Reservation 3 Years"
                    ]:
                        joined_df[cost_col] = joined_df[cost_col] / joined_df["vCPUs"]
                elif selected_pricing =="Memory":
                    for cost_col in [
                        "Linux On Demand Cost", "Linux Spot Cost", "Windows On Demand Cost", 
                        "Windows Spot Cost", "Linux Savings Price 1 Year", "Linux Savings Price 3 Years",
                        "Linux Reservation 1 Year", "Linux Reservation 3 Years",
                        "Windows Savings Price 1 Year", "Windows Savings Price 3 Years",
                        "Windows Reservation 1 Year", "Windows Reservation 3 Years"
                    ]:
                        joined_df[cost_col] = joined_df[cost_col] / joined_df["Instance Memory"]
            

                

                    
                st.dataframe(data = filter_dataframe(joined_df),height = 2000)
                

            else:
                st.error("No data retrieved from the query.")
    else:
        st.write("About")
