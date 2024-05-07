import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
import os
import folium
from streamlit_folium import st_folium
import json
from pathlib import Path

with open("assets/states.geojson") as f:
    states_geojson = json.load(f)

import folium
import json

import folium
import json

import streamlit as st
import folium
import json

# Load GeoJSON data for states
with open("assets/states.geojson") as f:
    states_geojson = json.load(f)

# Create a Folium map centered on the USA
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

# Add state boundaries to the map
folium.GeoJson(states_geojson, name="States").add_to(m)

# Define a Streamlit component wrapper for the Folium map
folium_map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
folium_map.add_child(folium.LatLngPopup())

# Render the Folium map in Streamlit using st.pydeck_chart()
st.pydeck_chart(folium_map)
