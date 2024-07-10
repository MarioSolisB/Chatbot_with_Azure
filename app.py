import streamlit as st

import os
import json
from langchain_openai import AzureChatOpenAI # from langchain.chat_models import AzureChatOpenAI < Langachain v0.2.0
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback




#################
# --- BACKEND ---
#################

# --- GET RESPONSE ---
def get_response(query, chat_history):
    template = """
        You are a helpful assistant. Answer the following question considering the history of conversation

        Chat history: {chat_history}

        User question: {user_question}
        """
    
    prompt = ChatPromptTemplate.from_template(template)

    llm = AzureChatOpenAI(
                deployment_name="gpt4-8k-jim2", #"gpt-3.5-turbo"  # Chatgpt model!
                #openai_api_type="azure",
                api_version="2024-02-15-preview",
                temperature=0.1
            )
    
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "chat_history": chat_history,
        "user_question": query
    })  
#    return chain.stream({
#        "chat_history": chat_history,
#        "user_question": query
#    })  

# --- LOAD JSON FILE ---
with open('keys.json', 'r') as file:
    data = json.load(file)



##################
# --- FRONTEND ---
##################
st.set_page_config(page_title="Chatbot Azure", page_icon="🤖")

st.title("ChatBot with Azure")

# --- Start session of chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Start session of button ---
if 'button_pressed' not in st.session_state:
    st.session_state.button_pressed = False

# --- Intialize the acumulate cost
if 'total_tokens'not in st.session_state:
    st.session_state.total_tokens = 0

if 'prompt_tokens' not in st.session_state:
        st.session_state.prompt_tokens = 0

if 'completion_tokens' not in st.session_state:
        st.session_state.completion_tokens = 0

if 'successful_requests' not in st.session_state:
        st.session_state.successful_requests= 0

if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0



azure_api_key = st.sidebar.text_input("Please, introduce your Azure API Key", type="password") 
submit_button = st.sidebar.button("Send Azure API key")

# --- Declare some states of button
if submit_button:
    if azure_api_key:
        st.success('Your provide an Azure API key')
        st.session_state.button_pressed = True
    else:
        st.error('Please introduce your Azure API key')
        st.session_state.button_pressed = False

# --- ACCESS TO API KEYS ---
MODEL = data["model"]
AZURE_ENDPOINT = data["AZURE_OPENAI_ENDPOINT"]
#AZURE_API_KEY = data["AZURE_OPENAI_API_KEY"]
API_VERSION = data["api_version"]

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_ENDPOINT
os.environ["AZURE_OPENAI_API_KEY"] = azure_api_key

# --- DEFINE THE main FUNCTION
def main():
    if st.session_state.button_pressed:
        # --- CONVERSATION ---
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.markdown(message.content)
            else:
                with st.chat_message("AI"):
                    st.markdown(message.content)



        user_query = st.chat_input("Your message")
        if user_query is not None and user_query !="":
            st.session_state.chat_history.append(HumanMessage(user_query))

            with st.chat_message("Humnan"):
                st.markdown(user_query)

            with st.chat_message("AI"):
                ai_response = get_response(user_query,st.session_state.chat_history)
                st.markdown(ai_response)
            
            st.session_state.chat_history.append(AIMessage(ai_response))
    

    else:
        st.write("Please, introduce a valide Azure API key in left box and click in 'Send Azure API key'.")


# --- main start ---
#####################################
# Python script execution starts here
if __name__ == '__main__':
    with get_openai_callback() as cost:
        main() # Calling the main function
        st.session_state.total_tokens += cost.total_tokens
        st.session_state.prompt_tokens += cost.prompt_tokens
        st.session_state.completion_tokens += cost.completion_tokens
        st.session_state.successful_requests += cost.successful_requests
        st.session_state.total_cost += cost.total_cost

        with st.sidebar:
            st.write(f"The total tokens are: {st.session_state.total_tokens}")
            st.write(f"The total prompt tokens are: {st.session_state.prompt_tokens}")
            st.write(f"The total completion tokens are: {st.session_state.completion_tokens}")
            st.write(f"The total successful requests are: {st.session_state.successful_requests}")
            st.write(f"The total cost is: $USD {st.session_state.total_cost:.4f}")
    
