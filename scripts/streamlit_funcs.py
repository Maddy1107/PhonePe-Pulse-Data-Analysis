# Import necessary libraries
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
import locale
import math

import scripts.constants as c
import scripts.sql_scripts as sql


# Streamlit page configuration
def set_page_config():
    st.set_page_config(
        page_title=c.page_title,
        page_icon=c.page_icon,
        layout="wide",
    )


# Setting page header
def set_page_header():
    st.markdown(
        f'<center><span style="color:white; font-size:30px">{c.page_header[0]}</span></center>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<center><span style="color:purple;font-size:24px">{c.page_header[1]}</span></center>',
        unsafe_allow_html=True,
    )


# Option nav menu
def set_option_menu():
    selected = option_menu(
        None,
        options=["Home", "Exploration", "Insights", "About"],
        # options =["",  "Analysis", "About"],
        icons=["house-fill", "tools", "bar-chart-fill", "person-fill"],
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "purple",
                "width": "100%",
            },
            "icon": {"color": "#000080", "font-size": "20px"},
            "nav-link": {
                "font-size": "20px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#800020",
            },
            "nav-link-selected": {"background-color": "green"},
        },
    )
    return selected


# Home option
def home(cursor):
    
    #Select type
    type_options = ["Transactions", "Users"]
    data_type = st.selectbox("Choose Type:[Transactions,User]", type_options)

    # Getting year list from a table
    year_list = sql.get_year_list("agg_transaction", cursor)

    #Select year and quarter    
    with st.popover('FILTER',use_container_width=True):
        year = st.selectbox("Choose year", year_list,index = len(year_list)-1)
        quarter = st.selectbox("Choose quarter", c.quarter_select_box,index = len(c.quarter_select_box)-1)
        quarter = int(quarter[1])
        
    #Dividing map and data to separate columns
    map_col, data_col = st.columns([5, 2])
    with map_col:
        if data_type == "Transactions":
            transaction_map(cursor, year, quarter)#Transaction data map
        else:
            user_map(cursor, year, quarter)#user data map
    with data_col:
        if data_type == "Transactions":
            transaction_data(cursor,year,quarter)#Show transaction 
        else:
            user_data(cursor)#Show user data


# Plot the map
def create_map_plot(df, color):
    show_legend = st.checkbox("Show_legend")

    fig = px.choropleth(
        df,
        geojson=c.geojson_url,
        featureidkey="properties.ST_NM",
        locations="state",
        color=color,
        color_continuous_scale="sunsetdark",
        hover_name="state",
        # hover_data=[color],
        projection="stereographic",
        title="fff",
    )

    fig.update_geos(fitbounds="locations", visible=False)

    if not show_legend:
        fig.update_coloraxes(showscale=False)

    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # import plotly.graph_objects as go

    # choropleth_data = go.Choropleth(
    # locations=['India','Nepal'],
    # z=[100, 200, 300],  # Values to be visualized
    # colorscale='Viridis',  # Color scale for visualization
    # colorbar=dict(title='Some title'),  # Color bar configuration
    # )
    # layout = go.Layout(
    # title='Choropleth Map',  # Title of the plot
    # geo=dict(
    #     showframe=False,  # Whether to show frame (plot border)
    #     showcoastlines=False,  # Whether to show coastlines
    #     projection_type='mercator'  # Type of projection
    #     )
    # )

    # fig = go.Figure(data=[choropleth_data], layout=layout)
    # st.plotly_chart(fig)


# Function for map visualize transactions
def transaction_map(cursor, year, quarter):
    query = f"select state, sum(Transaction_amount) as Total_amount from map_transaction where year = {year} and quarter = {quarter} group by state order by state"

    data = sql.execute_select(query, cursor)
    df = pd.DataFrame(data.fetchall(), columns=data.column_names)

    df["state"] = c.geojson_state_df

    create_map_plot(df, "Total_amount")


# Function for map visualize transactions
def user_map(cursor, year, quarter):
    pass

#Function to show transaction data
def transaction_data(cursor,year,quarter):

    with st.container(height = 500):
        
        #Total transaction data
        query = f"select year, quarter,sum(Transaction_count) as Total_Transactions,sum(Transaction_amount) as Total_amount,AVG(Transaction_amount) as Average_amount from agg_transaction where year = {year} and quarter = {quarter} group by year,quarter"
        trans_df = extract_convert_to_dataframe(query, cursor)

        total_transactions = trans_df["Total_Transactions"][0]
        total_amount = trans_df["Total_amount"][0]
        average_amount = total_amount / float(total_transactions)

        st.header("Transactions")
        st.write("All PhonePe transactions (UPI + Cards + Wallets)")
        st.markdown(
            f"<h3>{simplify_number(total_transactions,False)}</h3>", unsafe_allow_html=True
        )
        st.markdown(
            "<style>div.stDataFrame {font-size: 20px;}</style>", unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            st.write("Total payment value")
            st.markdown(
                f"<h3>₹{simplify_number(total_amount,True)}</h3>", unsafe_allow_html=True
            )
            st.markdown(
                "<style>div.stDataFrame {font-size: 10px;}</style>", unsafe_allow_html=True
            )

        with col2:
            st.write("Avg. transaction value")
            st.markdown(
                f"<h3>₹{simplify_number(average_amount,True)}</h3>", unsafe_allow_html=True
            )
            st.markdown(
                "<style>div.stDataFrame {font-size: 10px;}</style>", unsafe_allow_html=True
            )
            
        st.divider()
        
        #Type wise data
        query = f'select year, quarter, Transaction_type as type, sum(Transaction_amount) as Total_amount from agg_transaction where year = {year} and quarter = {quarter} group by year,quarter,Transaction_type'
        type_df = extract_convert_to_dataframe(query, cursor)
        
        st.header('Categories')
        for i,row in type_df.iterrows():
            type_name = row['type']
            type_amount = row['Total_amount']
            
            col1,col2 = st.columns(2)
            with col1:
                st.write(type_name)
            with col2:
                st.text(simplify_number(type_amount,True))
                
        st.divider()
        
        col1,col2,col3 = st.columns(3)
        
        with col1:
            state = st.button('States')
        with col2:
            district = st.button('Districts')
        with col3:
            pin = st.button('Postal Codes')
        
        state = True
        if(district):
            state =pin= False
        elif(pin):
            state =pin= False
        elif(state):
            state =pin= False  
        
        if state:
            st.header('Top 10 States')
            query = f'select state, sum(Transaction_amount) as total_amount from agg_transaction where year = {year} and quarter = {quarter} group by state order by total_amount desc Limit 10'
            state_df = extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                c1,c2,c3 = st.columns([1,10,6])
                with c1:
                    st.text(i+1)
                with c2:
                    st.write(row['state'])
                with c3:
                    st.text(simplify_number(row['total_amount'],True))
        if district:
            st.write('gdfgdjh')

#Function to show user data
def user_data(cursor):
    pass

#Function to extract from sql and convert to dataframe
def extract_convert_to_dataframe(query, cursor):
    data = sql.execute_select(query, cursor)
    return pd.DataFrame(data.fetchall(), columns=data.column_names)

#Function to convert numbers to comma separated and with Cr
def simplify_number(number, convert):
    locale.setlocale(locale.LC_NUMERIC, "en_IN")

    if convert:
        if number >= 1_00_00_000:
            cr_value = math.ceil(int(number / 1_00_00_000))
            formatted_cr_value = locale.format_string("%.0f", cr_value, grouping=True)
            return f"{formatted_cr_value} Cr"
    formatted_number = locale.format_string("%.0f", number, grouping=True)
    return f"{formatted_number}"
