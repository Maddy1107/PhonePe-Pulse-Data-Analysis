import json
from scripts import streamlit_funcs as st
from scripts import sql_scripts as sql

# Connect Database
cursor, mydb = sql.connect_database()

#Extracting the geoJson file
india_states = json.load(open('assets/india_state_geo.json'))

st.set_page_config()

st.set_page_header()

option_selected = st.set_option_menu()

if option_selected == 'Home':
    st.home(cursor)