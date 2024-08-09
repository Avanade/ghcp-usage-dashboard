import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Uses Azure Open AI GPT-4-Turbo
# Make sure you have a running Azure OpenAI service and the credentials are set in the .env file

# Azure OpenAI API credentials
client = AzureOpenAI(
  azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT'), 
  api_key=os.environ.get('AZURE_OPENAI_API_KEY'),  
  api_version="2024-02-15-preview"
)

def get_response_prod_calc(text):

    chat_history = [   
        {"role": "system", "content": "You are a helpful assistant tasked with analyzing the projected impact of GitHub Copilot on the user's development team productivity. Once the user provides data or observations, Start with  a forward-looking statement regarding the anticipated influence on productivity. Next is to Emphasize on key observations that can help on decision making. Lastly, Provide suggestions on how to further improve the productivity impact. Your responses must employ the future tense to reflect the predictive nature of the analysis."},
        {"role": "user", "content": text}
    ]

    # TODO: Tweak the max_tokens and temperature parameters
    max_tokens = 4096
    temperature = 1

    # Use chatCompletion 
    response = client.chat.completions.create(
        model=os.environ.get('AZURE_OPENAI_ENGINE'),
        messages = chat_history,
        max_tokens=max_tokens,
        temperature=temperature,        
        stop=None,
        frequency_penalty=0,
        presence_penalty=0)
    
    return response.choices[0].message.content, response.usage.total_tokens

def get_analysis_from_usage(data_str):
    chat_history = [
        {"role": "system", "content": "You are a GitHub Copilot Subject Matter Expert. Your task is to analyze the provided GitHub Copilot usage data and deliver comprehensive insights. Focus on the following areas:\n\nAdoption Trends: Explore how GitHub Copilot adoption has evolved over time, highlighting any significant increases or decreases.\n\nUsage Patterns: Examine trends in how users interact with suggestions, including the frequency and type of suggestions made.\n\nAcceptance Analysis: Break down the acceptance rate of suggestions, identifying high and low acceptance scenarios and possible reasons.\n\nKey Metrics: Evaluate critical metrics such as the average number of active users and the average acceptance rate, and discuss their implications.\n\nUser Segmentation: If possible, segment the user base to see if different groups (e.g., beginners vs. experienced developers) have varying usage patterns.\n\nLanguage-Based Aggregations:\n- Total suggestions made per language.\n- Total acceptances per language.\n- Total lines suggested per language.\n- Total active users per language.\n\nEditor-Based Aggregations:\n- Total suggestions made per editor.\n- Total acceptances per editor.\n- Total lines suggested per editor.\n- Total active users per editor.\n\nMake sure to provide actionable insights that can guide future developments and improvements of GitHub Copilot.\n\n Respond in a clear and concise format, using bullet points or numbered lists to organize your insights.\n\nWhen you display a numerical value, make sure to highlight it in **bold** to draw attention to the key data points."},
        {"role": "user", "content": f"# GitHub Copilot usage data:\n\n{data_str}"}
    ]

    max_tokens = 4096
    temperature = 0.2

    response = client.chat.completions.create(
        model=os.environ.get('AZURE_OPENAI_ENGINE'),
        messages=chat_history,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content, response.usage.total_tokens
