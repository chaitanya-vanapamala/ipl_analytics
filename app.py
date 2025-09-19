import streamlit as st
from dotenv import load_dotenv

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ipl_agent.agent import ask, create_history
from ipl_agent.config import Config
from ipl_agent.models import create_llm
from ipl_agent.tools import get_available_tools, with_sql_cursor

load_dotenv()

@st.cache_resource(show_spinner=False)
def get_model() -> BaseChatModel:
    llm = create_llm(Config.MODEL)
    llm = llm.bind_tools(get_available_tools())
    return llm

st.set_page_config(
    page_title="IPL Analyzer",
    layout="centered"
)

st.title("IPL Statistics Analyzer")

if "messages" not in st.session_state:
    st.session_state.messages = create_history()

for message in st.session_state.messages:
    if type(message) is SystemMessage:
        continue

    is_user = type(message) is HumanMessage
    avatar = "👤" if is_user else "🤖"
    with st.chat_message("You" if is_user else "AI", avatar=avatar):
        st.markdown(message.content)


if prompt := st.chat_input("Type you query..."):
    with st.chat_message("user", avatar="👤"):
        st.session_state.messages.append(HumanMessage(prompt))
        st.markdown(prompt)
    
    with st.chat_message("AI", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.status("Retriving results, Please wait...", state="running")

        response = ask(prompt, st.session_state.messages, get_model())
        message_placeholder.markdown(response)
        st.session_state.messages.append(AIMessage(response))