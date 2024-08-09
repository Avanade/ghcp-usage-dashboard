import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from helpers.openai import get_response_prod_calc, get_analysis_from_usage
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Cache dictionary
cache = {
    "data": None,
    "expiry": None
}

# Cache expiry time (e.g., 10 minutes)
CACHE_EXPIRY = timedelta(minutes=10)

# Get the GitHub token and organization name from environment variables
TOKEN = os.getenv('GHCP_TOKEN')
ORG_NAME = os.getenv('ORG_NAME')

# Set the headers
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}

# Initialize an empty list to store all seats
all_seats = []

# Set the API endpoint for number of users
billing_users_url = f"https://api.github.com/orgs/{ORG_NAME}/copilot/billing"
usage_url = f"https://api.github.com/orgs/{ORG_NAME}/copilot/usage"

def get_response_from_usage():
    # Call the API to get the usage data
    response = requests.get(usage_url, headers=headers)

    # Parse the JSON response
    data = response.json()

    # Send data to Azure OpenAI
    #send_data_to_openai(data)

    # Update the cache
    cache["data"] = data
    cache["expiry"] = datetime.now() + CACHE_EXPIRY

    return data

# Get Usage Data
data = get_response_from_usage()

# Function to get the Copilot usage
def get_copilot_usage():
    # Call the API to get the number of users
    response = requests.get(billing_users_url, headers=headers)

    # Parse the JSON response
    data = response.json()
    seat_breakdown = data['seat_breakdown']
    added_this_cycle = seat_breakdown['added_this_cycle']
    active_this_cycle = seat_breakdown['active_this_cycle']
    inactive_this_cycle = seat_breakdown['inactive_this_cycle']
    total = seat_breakdown['total']

    return added_this_cycle, active_this_cycle, inactive_this_cycle, total

def get_copilot_average_acceptance_rate():

    # Initialize counters for total lines suggested and accepted
    total_lines_suggested = 0
    total_lines_accepted = 0

    # Iterate over each item in the data
    for item in data:
        total_lines_suggested += item['total_suggestions_count']
        total_lines_accepted += item['total_acceptances_count']

    # Calculate the average acceptance rate
    average_acceptance_rate = total_lines_accepted / total_lines_suggested if total_lines_suggested else 0

    return average_acceptance_rate

def get_percentage_active_users_past_28_days():

    # Initialize counters for total active users and active users in the past 28 days
    total_active_users = 0
    active_users_past_28_days = 0

    # Get the date 28 days ago
    date_28_days_ago = datetime.now() - timedelta(days=28)

    # Iterate over each item in the data
    for item in data:
        day = datetime.strptime(item['day'], '%Y-%m-%d')
        total_active_users += item['total_active_users']
        if day >= date_28_days_ago:
            active_users_past_28_days += item['total_active_users']

    print(total_active_users, active_users_past_28_days)

    # Calculate the percentage of active users in the past 28 days
    percentage_active_users_past_28_days = (active_users_past_28_days / total_active_users) * 100 if total_active_users else 0

    return percentage_active_users_past_28_days

def get_average_active_and_chat_users():

    # Initialize counters for total active users and chat users
    total_active_users = 0
    total_active_chat_users = 0

    # Iterate over each item in the data
    for item in data:
        total_active_users += item['total_active_users']
        total_active_chat_users += item['total_active_chat_users']

    # Calculate the average active users and chat users
    average_active_users = total_active_users / len(data) if data else 0
    average_active_chat_users = total_active_chat_users / len(data) if data else 0

    return "{:.1f}".format(average_active_users), "{:.1f}".format(average_active_chat_users)


def get_acceptance_versus_suggested():

    # Initialize lists for days, suggestions, and acceptances
    days = []
    suggestions = []
    acceptances = []

    # Iterate over each item in the data
    for item in data:
        days.append(item['day'])
        suggestions.append(item['total_suggestions_count'])
        acceptances.append(item['total_acceptances_count'])

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'Day': days,
        'Suggestions': suggestions,
        'Acceptances': acceptances
    })

    # Create a line chart with Plotly
    fig = px.area(df, x='Day', y=['Acceptances','Suggestions'], title='Copilot Acceptances vs Suggestions', markers=True)

    # Update the layout to change the title font color
    fig.update_layout(title_font=dict(color='#1f77b4'))
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))

    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)



def get_active_users_by_day():

    # Initialize lists for days, active users, and active chat users
    days = []
    active_users = []
    active_chat_users = []

    # Iterate over each item in the data
    for item in data:
        days.append(item['day'])
        active_users.append(item['total_active_users'])
        active_chat_users.append(item['total_active_chat_users'])

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'Day': days,
        'Active Users': active_users,
        'Active Chat Users': active_chat_users
    })

    # Create a stacked bar chart with Plotly
    fig = px.bar(df, x='Day', y=['Active Users', 'Active Chat Users'], labels={'x':'Day', 'value':'Users'}, title='Active Users by Day', text='value', barmode='stack')

    # Update layout to show text on bars
    fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

def get_lines_accepted_versus_suggested():

    # Initialize lists for days, lines suggested, and lines accepted
    days = []
    lines_suggested = []
    lines_accepted = []

    # Iterate over each item in the data
    for item in data:
        days.append(item['day'])
        lines_suggested.append(item['total_lines_suggested'])
        lines_accepted.append(item['total_lines_accepted'])

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'Day': days,
        'Lines Suggested': lines_suggested,
        'Lines Accepted': lines_accepted
    })

    # Create a line chart with Plotly
    fig = px.area(df, x='Day', y=['Lines Accepted','Lines Suggested'], title='Lines of Code Accepted vs Lines Suggested', markers=True)

    # Update the layout to change the title font color
    fig.update_layout(title_font=dict(color='#1f77b4'))
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))

    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)

def get_acceptance_rate():

    # Initialize lists for days and acceptance rates
    days = []
    acceptance_rates = []

    # Iterate over each item in the data
    for item in data:
        days.append(item['day'])
        # Check if total_suggestions_count is not zero
        if item['total_suggestions_count'] != 0:
            # Calculate the acceptance rate and append it to the list
            acceptance_rate = round((item['total_acceptances_count'] / item['total_suggestions_count']) * 100, 1)
        else:
            acceptance_rate = 0
        acceptance_rates.append(acceptance_rate)

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'Day': days,
        'Acceptance Rate (%)': acceptance_rates
    })

    # Create a line chart with Plotly
    fig = px.area(df, x='Day', y='Acceptance Rate (%)', title='Acceptance Rate (%) by Day', markers=True)

    # Increase the height of the chart
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
    
    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)

def send_data_to_openai(data):
    # Convert data to a string format
    data_str = str(data)

    # Get response from Azure OpenAI
    response, tokens_used = get_analysis_from_usage(data_str)

    # Print the response and tokens used
    # print("Azure OpenAI Response:", response)
    # print("Tokens Used:", tokens_used)

    return response, tokens_used
