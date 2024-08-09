import streamlit as st
from dotenv import load_dotenv
import re
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from helpers.api import *
from helpers.charts import *
from PIL import Image
from helpers.api import send_data_to_openai
import os

# Set streamlit configuration to wide mode
st.set_page_config(layout="wide", page_title="GitHub Copilot Usage Dashboard")

# Define custom CSS for styles
st.markdown(
    """
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }
    .metrics-table th, .metrics-table td {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }

    div[data-testid="stMetricValue"] {
        color: #1f77b4;
        font-size:48px;
        padding: 0px; /* Adjust left and right padding */        
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        width: 50%;
        text-align: center;
        margin: 0 auto; /* Center contents horizontally */
    }   

    div[data-testid="column"] {
        text-align: center;
    }  

    label[data-testid="stMetricLabel"] {
        text-align: center;
        color: #1f77b4;
        font-weight: bold;
        font-size:36px;

    }  

    .title {
        color: #1f77b4;
        text-align: center;
    }
    .box {
        border: none;
        padding: 0px; /* Adjust left and right padding */        
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        margin: 0px;
        height: auto;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown('<h1 class="title">GitHub Copilot Usage Dashboard</h1>', unsafe_allow_html=True)
#st.write('GitHub Copilot REST API Documentation: https://docs.github.com/en/rest/copilot/copilot-usage?apiVersion=2022-11-28')

# Call the API to get the number of users
try:
    response = get_copilot_usage()

    # print(response)

    added_this_cycle, active_this_cycle, inactive_this_cycle, total = response[:4]

    # Change column definition    
    bcol = st.columns((1,1,1,1))

    with bcol[0]:        
        
        # Use HTML to change the font color
        st.markdown(
            '''
                <div class="box">
                <p style="color:#1f77b4; font-weight:bold; font-size:20px;">Copilot Users</p>
            ''', 
            unsafe_allow_html=True
        )   
        st.markdown('</div>', unsafe_allow_html=True)     
        generate_user_bar_chart(active_this_cycle, inactive_this_cycle, added_this_cycle, total)       

    with bcol[1]:
        # Display a gauge chart for active users
        st.markdown(
            '''
                <div>
                <p style="color:#1f77b4; font-weight:bold; font-size:20px;">Adoption Rate</p>
                </div>
            ''', 
            unsafe_allow_html=True
        )   
        
        create_gauge_chart(active_this_cycle / total * 100, 80)

    with bcol[2]:
        # Display a gauge chart for active users
        st.markdown(
            '''
                <div>
                <p style="color:#1f77b4; font-weight:bold; font-size:20px;">Average Acceptance Rate</p>
                </div>
            ''', 
            unsafe_allow_html=True
        )   
        
        create_gauge_chart(get_copilot_average_acceptance_rate() * 100, 50)              

    with bcol[3]:
        # Display the number of active users
        st.markdown(
            '''
                <div class="box">
                <p style="color:#1f77b4; font-weight:bold; font-size:20px;">Usage Adoption Key Metrics</p>
                </div>
            ''', 
            unsafe_allow_html=True
        )   
       
        # Assuming get_average_active_and_chat_users() returns a list of two values
        average_active_users, average_chat_users = get_average_active_and_chat_users()

        st.metric("Average Active Users", average_active_users)
        st.metric("Average Chat Users", average_chat_users)

    # Create 2 columns
    ccol1, ccol2 = st.columns(2)

    with ccol1:
        
        get_active_users_by_day()
    
        get_lines_accepted_versus_suggested()

    with ccol2:        
        get_acceptance_versus_suggested()

        get_acceptance_rate()
    
    # Get the usage data from API
    usage_response = get_response_from_usage()
    #print(usage_response[0])
    # Display usage data in a table

    with st.expander("View Usage Data"):
        display_flattened_usage_data(usage_response)

    # Add a button to trigger the analysis
    if st.button('AI-Powered Data Analysis'):        
        
        # print(usage_response)
        # Check if the API key exists in the environment variables
        if os.environ.get('AZURE_OPENAI_API_KEY'):
            # Execute the highlighted code
            analysis = send_data_to_openai(usage_response)
            st.markdown('<h1 class="title">AI-Powered Insights on Usage Trends</h1>', unsafe_allow_html=True)
            st.write(analysis[0])
            st.write("Total Tokens Used: ", analysis[1])
        else:
            st.error("You need an Azure OpenAI API Endpoint and Key to use this feature.")

except Exception as e:
    st.error(f"Error Fetching Data: {str(e)}")
