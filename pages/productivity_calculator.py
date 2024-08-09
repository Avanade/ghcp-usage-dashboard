import streamlit as st
import os
from helpers.openai import get_response_prod_calc

# Function to perform calculations
def calculate_metrics(number_of_developers, total_loaded_cost, total_hours, percent_coding, hourly_rate, percent_time_saved, percent_adoption):
    devs_using_copilot = number_of_developers * (percent_adoption / 100)
    hours_coding = number_of_developers * total_hours * (percent_coding / 100) * (percent_adoption / 100)
    hours_not_coding = (number_of_developers * total_hours * (percent_adoption / 100)) - hours_coding
    time_saved = percent_time_saved / 100 * hours_coding
    net_productivity_gain = time_saved / (hours_coding + hours_not_coding)
    adopter_coding_productivity_gain = percent_time_saved
    adopter_total_productivity_gain = net_productivity_gain * 100
    increase_in_adopter_velocity = (hours_coding + hours_not_coding) / (hours_coding + hours_not_coding - time_saved)
    time_saved_as_dollars = time_saved * hourly_rate
    reduced_duration_of_delay = net_productivity_gain * 100  # Assuming 10% based on study
    reduced_chance_of_failure = 10  # Assuming 10% based on study    

    return {
        'devs_using_copilot': devs_using_copilot,
        'hours_coding': hours_coding,
        'hours_not_coding': hours_not_coding,
        'time_saved': time_saved,
        'adopter_coding_productivity_gain': adopter_coding_productivity_gain,
        'adopter_total_productivity_gain': adopter_total_productivity_gain,
        'increase_in_adopter_velocity': increase_in_adopter_velocity,
        'time_saved_as_dollars': time_saved_as_dollars,
        'reduced_duration_of_delay': reduced_duration_of_delay,
        'reduced_chance_of_failure': reduced_chance_of_failure,
    }

streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Inter:slnt@-10..0&display=swap')

			body {
                font-family: 'Inter', sans-serif;
                font-style: normal;
                font-variation-settings:
            }
			</style>
			"""

# Page Configuration
st.set_page_config(
    page_title="Productivity Impact Calculator",
    page_icon=":chart_with_upwards_trend:",
    layout='wide',
    initial_sidebar_state='auto'
)

# Streamlit app layout
st.image("images/purple_gh_copilot.png", width=96,)
st.markdown("<h2 style='color: #1f77b4;'>Productivity Impact Calculator</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #1f77b4;'>Calculate the potential productivity impact of GitHub Copilot on your development team</p>", unsafe_allow_html=True)

st.markdown(streamlit_style, unsafe_allow_html=True)

# User Entries
with st.sidebar:
    st.header("Input Metrics to the Calculator")
    company_name = st.text_input("Company Name", placeholder="Enter Company Name")
    number_of_developers = st.number_input("Number of Developers", value=700, help="Count of Total Developers")
    total_loaded_cost = st.number_input("Total Loaded Cost per dev per Year", value=100000, step=100, format="%d", help="Salary + Benefits + Other Expenses")
    total_hours = st.number_input("Total Hours Available per Dev per Year", value=2000, step=10, help="Hours (defaults to 2000 hrs for 1 yr)")
    hourly_rate_calc = total_loaded_cost / total_hours
    percent_coding = st.number_input("Percent of day/week/year Spent Coding", value=40.00, step=5.00, min_value=5.00, max_value=100.00, help="% of Total time spent Coding (SCRUM suggests expecting 6 hours per 8 hour day or 75%)")
    hourly_rate = st.number_input("Hourly Rate", value=hourly_rate_calc, step=5.00, min_value=5.00, max_value=100.00, help="Dollars/Hour calculated from Total Loaded cost / hours available per dev")
    percent_time_saved = st.number_input("% of Time saved per task", value=25.00, step=5.00, min_value=5.00, max_value=1000.00, help="% time saved (if a 10 hour task takes 4 hours w/Copilot the % would be 60%)")
    percent_adoption = st.number_input("Percent adoption", value=90.00, step=5.00, min_value=5.00, max_value=100.00, help="% of Total Devs Using GH CoPilot")

    calculate = st.button("Calculate")

# Button to perform calculation
if not company_name:
    st.error('Company name is required')
elif calculate:
    results = calculate_metrics(number_of_developers, total_loaded_cost, total_hours, percent_coding, hourly_rate, percent_time_saved, percent_adoption)

    # Display results
    st.markdown(f"""
        <style>
        table {{
            width:100%;
        }}
        th {{
            background-color: #0078D4;
            color: #ffffff;
        }}
        </style>
        <h2 style='color: #1f77b4;'>Results for {company_name}</h2>
        <table>
        <tr>
        <th>Metric</th>
        <th>Value</th>
        <th>Description</th>
        </tr>
        <tr>
        <td>Developers Using Copilot</td>
        <td>{int(results['devs_using_copilot'])}</td>
        <td>This is the number of developers in your organization who are using GitHub Copilot.</td>
        </tr>
        <tr>
        <td>Hours Coding (before Copilot)</td>
        <td>{int(results['hours_coding']):,}</td>
        <td>Developer Capacity in hours per year.</td>
        </tr>
        <tr>
        <td>Hours Not Coding</td>
        <td>{int(results['hours_not_coding']):,}</td>
        <td>Time not Developing in hours per year.</td>
        </tr>
        <tr>
        <td>Time Saved</td>
        <td>{int(results['time_saved']):,}</td>
        <td>Hours per year saved.</td>
        </tr>
        <tr>
        <td>Adopter Coding Productivity Gain</td>
        <td>{results['adopter_coding_productivity_gain']:.2f}%</td>
        <td>% of time saved for coding activities when using Copilot.</td>
        </tr>
        <tr>
        <td>Adopter Total Productivity Gain</td>
        <td>{results['adopter_total_productivity_gain']:.2f}%</td>
        <td>% of time saved for a scope of work when including Copilot.</td>
        </tr>
        <tr>
        <td>Increase in Adopter Velocity</td>
        <td>{results['increase_in_adopter_velocity']:.2f}</td>
        <td>Units/Cycles Delivered in Same Timeframe.</td>
        </tr>
        <tr>
        <td>Time Saved as Dollars</td>
        <td>${int(results['time_saved_as_dollars']):,}</td>
        <td>Economic Benefit in Dollars per Year.</td>
        </tr>
        <tr>
        <td>Reduced Duration of Unexpected Coding Delays</td>
        <td>{results['reduced_duration_of_delay']}%</td>
        <td>Less time spent on Unexpected Coding Delays.</td>
        </tr>
        <tr>
        <td>Reduced Chance of Failure</td>
        <td>{results['reduced_chance_of_failure']}%</td>
        <td>Less chance of Not Completing Task.</td>
        </tr>
        </table>
        <br/>
    """, unsafe_allow_html=True)

    markdown_text = f"""
    # Results for {company_name}

    ## Intermediate Calculations
    **Developers Using Copilot:** <span style='color:green; font-size:150%'>**{int(results['devs_using_copilot'])}**</span>
    <sub>This is the number of developers in your organization who are using GitHub Copilot.</sub>

    **Hours Coding (before Copilot):** <span style='color:green; font-size:150%'>**{int(results['hours_coding']):,}**</span>
    <sub>Developer Capacity in hours Year.</sub>

    **Hours Not Coding:** <span style='color:green; font-size:150%'>**{int(results['hours_not_coding']):,}**</span>
    <sub>Time not Developing in hours Year.</sub>

    ## Business Value Calculations
    **Time Saved:** <span style='color:green; font-size:150%'>**{int(results['time_saved']):,}**</span> Hours per Year
    <sub>Hours per year saved.</sub>

    **Adopter Coding Productivity Gain:** <span style='color:green; font-size:150%'>**{results['adopter_coding_productivity_gain']}%**</span>
    <sub>% of time saved for coding activities when using Copilot.</sub>

    **Adopter Total Productivity Gain:** <span style='color:green; font-size:150%'>**{results['adopter_total_productivity_gain']:.2f}%**</span>
    <sub>% of time saved for a scope of work when including Copilot.</sub>

    **Increase in Adopter Velocity:** <span style='color:green; font-size:150%'>**{results['increase_in_adopter_velocity']:.2f}**</span>
    <sub>Units/Cycles Delivered in Same Timeframe.</sub>

    ## Cost
    **Time Saved as Dollars:** <span style='color:green; font-size:150%'>**${int(results['time_saved_as_dollars']):,}**</span>
    <sub>Economic Benefit in Dollars per Year.</sub>

    ## Risk
    **Reduced Duration of Unexpected Coding Delays:** <span style='color:green; font-size:150%'>**{results['reduced_duration_of_delay']}%**</span>
    <sub>Less time spent on Unexpected Coding Delays.</sub>

    **Reduced Chance of Failure:** <span style='color:green; font-size:150%'>**{results['reduced_chance_of_failure']}%**</span>
    <sub>Less chance of Not Completing Task.</sub>


    """
   
    ## Checks for Azure OpenAI API key if exists    
    if 'AZURE_OPENAI_API_KEY' in os.environ and os.environ['AZURE_OPENAI_API_KEY']:
        st.markdown("<h2 style='color: #1f77b4;'>Further Analysis</h2>", unsafe_allow_html=True)
        with st.spinner("Processing..."):        
            st.write(get_response_prod_calc(markdown_text)[0])
    else:
        st.warning("Azure OpenAI API key not found. Further analysis cannot be performed.")
    

VERSION = "[Build.Id]"  

footer = f"""<div style="position: fixed; bottom: 10px; right: 10px; font-size: 0.8rem; font-weight: bold; color: #fafafa;">Version: {VERSION}</div>"""  
st.markdown(footer, unsafe_allow_html=True)  