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
usage_url = f"https://api.github.com/orgs/{ORG_NAME}/copilot/metrics"

def get_response_from_usage():
    try:
        response = requests.get(usage_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Update cache
        cache["data"] = data
        cache["expiry"] = datetime.now() + CACHE_EXPIRY
        
        return data
    except requests.RequestException as e:
        st.error(f"Error fetching usage data: {str(e)}")
        return None

def process_metrics_data(data):
    if not data:
        return pd.DataFrame()
    
    # Initialize lists to store flattened data
    records = []
    
    for daily_data in data:
        # Process IDE code completions
        if 'copilot_ide_code_completions' in daily_data:
            for editor in daily_data['copilot_ide_code_completions'].get('editors', []):
                for model in editor.get('models', []):
                    for lang in model.get('languages', []):
                        records.append({
                            'date': daily_data['date'],
                            'feature_type': 'ide_code',
                            'editor': editor['name'],
                            'model_name': model['name'],
                            'is_custom_model': model['is_custom_model'],
                            'language': lang['name'],
                            'engaged_users': lang['total_engaged_users'],
                            'suggestions': lang.get('total_code_suggestions', 0),
                            'acceptances': lang.get('total_code_acceptances', 0),
                            'lines_suggested': lang.get('total_code_lines_suggested', 0),
                            'lines_accepted': lang.get('total_code_lines_accepted', 0)
                        })
        
        # Process IDE chat
        if 'copilot_ide_chat' in daily_data:
            for editor in daily_data['copilot_ide_chat'].get('editors', []):
                for model in editor.get('models', []):
                    records.append({
                        'date': daily_data['date'],
                        'feature_type': 'ide_chat',
                        'editor': editor['name'],
                        'model_name': model['name'],
                        'is_custom_model': model['is_custom_model'],
                        'engaged_users': model['total_engaged_users'],
                        'total_chats': model.get('total_chats', 0),
                        'chat_insertions': model.get('total_chat_insertion_events', 0),
                        'chat_copies': model.get('total_chat_copy_events', 0)
                    })
        
        # Process dotcom chat
        if 'copilot_dotcom_chat' in daily_data:
            for model in daily_data['copilot_dotcom_chat'].get('models', []):
                records.append({
                    'date': daily_data['date'],
                    'feature_type': 'dotcom_chat',
                    'editor': 'github.com',
                    'model_name': model['name'],
                    'is_custom_model': model['is_custom_model'],
                    'engaged_users': model['total_engaged_users'],
                    'total_chats': model.get('total_chats', 0)
                })
        
        # Process PR data
        if 'copilot_dotcom_pull_requests' in daily_data:
            for repo in daily_data['copilot_dotcom_pull_requests'].get('repositories', []):
                for model in repo.get('models', []):
                    records.append({
                        'date': daily_data['date'],
                        'feature_type': 'pull_requests',
                        'repository': repo['name'],
                        'model_name': model['name'],
                        'is_custom_model': model['is_custom_model'],
                        'engaged_users': model['total_engaged_users'],
                        'pr_summaries': model.get('total_pr_summaries_created', 0)
                    })
    
    return pd.DataFrame(records)

def get_copilot_stats():
    data = get_response_from_usage()
    if not data:
        return pd.DataFrame()
    
    df = process_metrics_data(data)
    return df

def get_acceptance_versus_suggested():
    df = get_copilot_stats()
    if df.empty:
        return
    
    # Filter for IDE code completions and aggregate by date
    ide_code_df = df[df['feature_type'] == 'ide_code'].groupby('date').agg({
        'suggestions': 'sum',
        'acceptances': 'sum'
    }).reset_index()
    
    # Create the visualization
    fig = px.area(ide_code_df, 
                  x='date', 
                  y=['acceptances', 'suggestions'],
                  title='Copilot Acceptances vs Suggestions',
                  markers=True)
    
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
    st.plotly_chart(fig, use_container_width=True)

def get_lines_accepted_versus_suggested():
    df = get_copilot_stats()
    if df.empty:
        return
    
    # Filter for IDE code completions and aggregate by date
    ide_code_df = df[df['feature_type'] == 'ide_code'].groupby('date').agg({
        'lines_suggested': 'sum',
        'lines_accepted': 'sum'
    }).reset_index()
    
    # Create the visualization
    fig = px.area(ide_code_df,
                  x='date',
                  y=['lines_accepted', 'lines_suggested'],
                  title='Lines of Code Accepted vs Lines Suggested',
                  markers=True)
    
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
    st.plotly_chart(fig, use_container_width=True)

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
    df = get_copilot_stats()
    if df.empty:
        return 0
    
    # Filter for IDE code completions
    ide_code_df = df[df['feature_type'] == 'ide_code']
    
    # Calculate totals
    total_suggestions = ide_code_df['suggestions'].sum()
    total_acceptances = ide_code_df['acceptances'].sum()
    
    # Calculate the average acceptance rate
    return total_acceptances / total_suggestions if total_suggestions else 0

def get_percentage_active_users_past_28_days():
    df = get_copilot_stats()
    if df.empty:
        return 0
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Get the date 28 days ago
    date_28_days_ago = datetime.now() - timedelta(days=28)
    
    # Get unique counts of engaged users
    total_engaged = df['engaged_users'].sum()
    recent_engaged = df[df['date'] >= date_28_days_ago]['engaged_users'].sum()
    
    return (recent_engaged / total_engaged * 100) if total_engaged else 0

def get_average_active_and_chat_users():
    df = get_copilot_stats()
    if df.empty:
        return "0", "0"
    
    # Calculate average engaged users for IDE code and chat
    avg_ide_users = df[df['feature_type'] == 'ide_code']['engaged_users'].mean()
    avg_chat_users = df[df['feature_type'].isin(['ide_chat', 'dotcom_chat'])]['engaged_users'].mean()
    
    return "{:.1f}".format(avg_ide_users or 0), "{:.1f}".format(avg_chat_users or 0)

def get_active_users_by_day():
    df = get_copilot_stats()
    if df.empty:
        return
    
    # Aggregate users by date and feature type
    daily_users = df.groupby(['date', 'feature_type'])['engaged_users'].sum().reset_index()
    
    # Pivot the data for plotting
    plot_df = daily_users.pivot(index='date', columns='feature_type', values='engaged_users').reset_index()
    plot_df = plot_df.fillna(0)
    
    # Create a stacked bar chart with Plotly
    fig = px.bar(plot_df, 
                 x='date', 
                 y=['ide_code', 'ide_chat', 'dotcom_chat'], 
                 title='Active Users by Day',
                 labels={'value': 'Users'},
                 barmode='stack')
    
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
    st.plotly_chart(fig, use_container_width=True)

def get_acceptance_rate():
    df = get_copilot_stats()
    if df.empty:
        return
    
    # Filter for IDE code completions and calculate daily acceptance rates
    ide_code_df = df[df['feature_type'] == 'ide_code'].groupby('date').agg({
        'suggestions': 'sum',
        'acceptances': 'sum'
    }).reset_index()
    
    # Calculate acceptance rate
    ide_code_df['Acceptance Rate (%)'] = (ide_code_df['acceptances'] / ide_code_df['suggestions'] * 100).round(1)
    
    # Create the visualization
    fig = px.area(ide_code_df, 
                  x='date', 
                  y='Acceptance Rate (%)', 
                  title='Acceptance Rate (%) by Day',
                  markers=True)
    
    fig.update_layout(height=400, title_font=dict(color='#1f77b4'))
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
