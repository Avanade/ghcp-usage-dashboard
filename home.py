import streamlit as st
# import other necessary libraries

# Create 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    # Image images\GitHub-Copilot.jpeg
    st.image('images/GitHub-Copilot.jpeg', use_column_width=True)

# Create a sidebar for feature selection
st.sidebar.success('Select a feature above')

st.markdown(
    """
    ## GitHub Copilot Utilities

    ### 1. GitHub Copilot Productivity Calculator 
        
    > This calculator estimates the potential productivity impact of GitHub Copilot on your development team. 

    ### 2. GitHub Copilot Usage Dashboard
        
    > Analyze your GitHub Copilot usage to understand how it's being used in your organization.

    To get started, select a feature from the sidebar on the left. Enjoy exploring the capabilities of AI!

    """
)

# Display the app version number in the footer
VERSION = "[Build.Id]"  

footer = f"""<div style="position: fixed; bottom: 10px; right: 10px; font-size: 0.8rem; font-weight: bold; color: #fafafa;">Version: {VERSION}</div>"""  
st.markdown(footer, unsafe_allow_html=True)  