import streamlit as st
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
import requests

# Set up API keys
openai_api_key = "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"
google_api_key = "AIzaSyBlKL7gdT7HuzIVszBnhZ9qZY8h_4auyZM"
google_cse_id = "6280b1ce3068249a8"

# Initialize the OpenAI Chat Model (GPT-4)
llm = ChatOpenAI(
    model="gpt-4",  # Use "gpt-3.5-turbo" if GPT-4 is unavailable
    temperature=0.7,
    openai_api_key=openai_api_key
)

# Define the Google Search Tool
def google_search_tool(query):
    """Use Google Custom Search API to fetch search results."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": google_cse_id,
        "q": query,
        "num": 3  # Limit to top 3 results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        if results:
            return "\n".join([f"{item['title']}: {item['link']}" for item in results])
        else:
            return "No results found."
    else:
        return f"Failed to fetch results: {response.text}"

# Define tools for the agent
tools = [
    Tool(
        name="Google Search",
        func=google_search_tool,
        description="Search the web for information."
    )
]

# Create the LangChain agent
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

# Streamlit UI
st.title("AI Agent with LangChain")
st.markdown(
    """
    ### Welcome to your AI-powered assistant!
    - Enter any question or query.
    - The agent will use OpenAI GPT-4 and Google Search to provide an answer.
    """
)

# Input text box
user_query = st.text_input("Enter your question:")

if st.button("Submit"):
    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Run the agent with the user's query
                agent_response = agent.run(user_query)
                st.success("Response:")
                st.write(agent_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
