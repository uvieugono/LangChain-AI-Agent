import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from supabase import create_client, Client

# Load secrets from Streamlit Secrets Manager
openai_api_key = st.secrets["OPENAI_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o-mini"
    openai_api_key=openai_api_key,
    temperature=0.5
)

# System message for guiding the chatbot
system_message = """
You are an AI Customer Service Representative for Solynta Energy.
You handle payment and system-related inquiries for existing customers.
Always verify the customer's phone number and fetch their details before proceeding.
"""

# Function to query customer data from Supabase
def verify_customer(phone_number):
    """
    Query the Supabase database to verify if a customer exists.
    """
    response = supabase.table("customers").select("*").eq("phone_number", phone_number).execute()
    if response.data:
        customer = response.data[0]
        name = customer["customer_name"]
        account_status = customer["account_status"]
        token_status = customer["token_status"]
        return f"Customer found: {name}. Account status: {account_status}, Token status: {token_status}."
    else:
        return "No customer found with this phone number. Please check and try again."

# Define tools for the agent
tools = [
    Tool(
        name="Verify Customer",
        func=verify_customer,
        description="Verify if a user is an existing customer using their phone number."
    )
]

# Create the LangChain agent
agent = initialize_agent(
    tools,
    llm,
    agent_type="zero-shot-react-description",
    verbose=True,
    system_prompt=system_message
)

# Streamlit app interface
st.title("Solynta Energy Customer Service")
st.write("This chatbot assists existing customers with payment and system-related inquiries.")

# Input for customer phone number
phone_number = st.text_input("Enter your registered phone number:")

# Input for customer query
query = st.text_input("Enter your question or issue:")
if st.button("Submit"):
    if phone_number:
        verification_result = verify_customer(phone_number)
        st.write(verification_result)
        if "Customer found" in verification_result:
            try:
                response = agent.run(query)
                st.write("Response:")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Unable to verify your account. Please provide the correct phone number.")
    else:
        st.error("Please provide your registered phone number.")
