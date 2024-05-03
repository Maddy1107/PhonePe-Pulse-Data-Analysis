import streamlit as st

# Define a function to apply background color to a column
def apply_background_color(color):
    return f'<div style="background-color:{color}; padding: 5px"></div>'

# Example usage
colored_text = apply_background_color("#ffcccb", "This is a pink column")
st.markdown(colored_text, unsafe_allow_html=True)
