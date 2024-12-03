import os
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

# Validate API keys
if not openai_api_key or not google_api_key or not google_cse_id:
    st.error("API keys are not properly configured. Please check your environment variables.")
    st.stop()

# Define the search tool using Google Search API
def google_search_tool(query: str) -> str:
    import requests

    # Make a request to Google Search API
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={google_cse_id}"
    response = requests.get(url)

    # Handle errors or return search results
    if response.status_code != 200:
        return f"Error: Unable to fetch results from Google Search API. {response.text}"
    results = response.json().get("items", [])
    if not results:
        return "No results found."
    
    # Return the first result as an example
    return results[0].get("snippet", "No description available.")

# Initialize LangChain tools
tools = [
    Tool(
        name="Google Search",
        func=google_search_tool,
        description="Use this tool to search the web using Google Custom Search API."
    )
]

# Initialize the OpenAI-powered agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=openai_api_key)
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

# Streamlit app UI
st.title("AI Agent with LangChain")
st.markdown("""
### Welcome to your AI-powered assistant!
- Enter any question or query.
- The agent will use OpenAI GPT-4 and Google Search to provide an answer.
""")

# Input field
user_input = st.text_input("Enter your question:", "")

if st.button("Submit"):
    if user_input.strip():
        with st.spinner("Processing your request..."):
            try:
                response = agent.run(user_input)
                st.success("Here is the response:")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question before submitting.")
