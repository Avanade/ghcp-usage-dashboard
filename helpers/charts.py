import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Function to plot the data
def plot_data(active, total, color_active, color_total):
    # Calculate the number of inactive licenses
    inactive = total - active

    # Create a pandas DataFrame
    df = pd.DataFrame({
        'Category': [''],
        'Active': [active],
        'Inactive': [inactive]
    })

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(12, 1))

    # Set the figure and axes background color to none
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

    # Plot the data
    ax.barh(df['Category'], df['Active'], color=color_active)
    ax.barh(df['Category'], df['Inactive'], left=df['Active'], color=color_total)

    # Display the number of active licenses inside the bar
    #ax.text(active / 2, 0, str(active), color='white', va='center')

    # Remove labels
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_yticks([])
    ax.set_xticks([])

    # Set title
    ax.title.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    return fig

def generate_user_bar_chart(active_this_cycle, inactive_this_cycle, added_this_cycle, total):
    
    # Create a DataFrame from the values
    df = pd.DataFrame({
        'Category': ['Active', 'Inactive', 'Added', 'Total'],
        'Value': [active_this_cycle, inactive_this_cycle, added_this_cycle, total]
    })

    # Reverse the DataFrame
    df = df.iloc[::-1]

    # Create the horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust the size of the plot

    # Get the current theme
    theme = st.get_option("theme.base")

    # Set the font color based on the theme
    font_color = "#1f77b4"

    # Change the background color and the label color
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    plt.rcParams['text.color'] = font_color
    plt.rcParams['axes.labelcolor'] = font_color
    plt.rcParams['xtick.color'] = font_color
    plt.rcParams['ytick.color'] = font_color

    # Use a color palette with shades of blue
    colors = ['#1f77b4', '#aec7e8', '#5dade2', '#2874a6']

    bars = ax.barh(df['Category'], df['Value'], height=0.8, color=colors)
    plt.yticks(fontsize=20)  # Adjust the size of the labels
    plt.xticks(fontsize=20)

    # Add grid lines for better readability
    ax.xaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.7)

    # Remove the box around the plot
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Add padding to the y-axis labels
    ax.tick_params(axis='y', pad=10)

    # Add data value labels inside each bar
    for bar in bars:
        width = bar.get_width()
        if width > 0:
            ax.text(width - 2, bar.get_y() + bar.get_height()/2, f'{width}', ha='right', va='center', color='white', fontsize=20)

    # Display the chart
    st.pyplot(fig)


def create_gauge_chart(value, threshold):
    # Get the current theme
    #theme = st.get_option("theme.base")

    font_color = "#1f77b4"
    gauge_color = "lightgray"

    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': font_color, 'tickmode': 'array', 'tickvals': [0, 25, 50, 75, 100]},
            'bar': {'color': '#1f77b4'},
            'bgcolor': gauge_color,
            'borderwidth': 2,
            'bordercolor': font_color,
            'steps': [
                {'range': [0, 100], 'color': '#aec7e8'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        },
        number={'suffix': "%", 'font': {'color': font_color}}
    ))

    # Adjust the size of the chart
    fig.update_layout(
        autosize=False,
        width=350,        
        height=280, 
        margin=dict(l=1, r=25, b=1, t=1),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': font_color}
    )

    # Display the chart
    st.plotly_chart(fig)

def generate_user_donut_chart(active_this_cycle, inactive_this_cycle, added_this_cycle, total):
    # Create a DataFrame from the values
    df = pd.DataFrame({
        'Category': ['Active', 'Inactive', 'Added', 'Total'],
        'Value': [active_this_cycle, inactive_this_cycle, added_this_cycle, total]
    })

    # Use a color palette with shades of blue
    colors = ['#1f77b4', '#aec7e8', '#5dade2', '#2874a6']

    # Create the donut chart
    fig, ax = plt.subplots(figsize=(4, 4))  # Adjust the size of the plot

    # Get the current theme
    theme = st.get_option("theme.base")

    # Set the font color based on the theme
    # if theme == "light":
    #     font_color = "black"
    # else:
    #     font_color = "white"

    font_color = "#1f77b4"
    # Change the background color and the label color
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    plt.rcParams['text.color'] = font_color
    plt.rcParams['axes.labelcolor'] = font_color

    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        df['Value'], 
        labels=df['Category'], 
        colors=colors, 
        autopct='%1.1f%%', 
        startangle=140, 
        pctdistance=0.85, 
        textprops={'color': font_color}
    )

    # Draw a circle at the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.35, fc='white')
    fig.gca().add_artist(centre_circle)

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')  

    # Add a title
    plt.title('User Distribution', color=font_color, fontsize=16)

    # Display the chart
    st.pyplot(fig)


def display_flattened_usage_data(data):
    # Initialize a list to store the flattened data
    flattened_data = []

    # Iterate over each item in the data
    for item in data:
        # Extract the common fields
        common_fields = {
            'day': item['day'],
            'total_suggestions_count': item['total_suggestions_count'],
            'total_acceptances_count': item['total_acceptances_count'],
            'total_lines_suggested': item['total_lines_suggested'],
            'total_lines_accepted': item['total_lines_accepted'],
            'total_active_users': item['total_active_users'],
            'total_chat_acceptances': item['total_chat_acceptances'],
            'total_chat_turns': item['total_chat_turns'],
            'total_active_chat_users': item['total_active_chat_users']
        }

        # Iterate over each breakdown item
        for breakdown in item['breakdown']:
            # Combine the common fields with the breakdown fields
            flattened_item = {**common_fields, **breakdown}
            flattened_data.append(flattened_item)

    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)

    # Display the DataFrame using Streamlit
    st.dataframe(df)