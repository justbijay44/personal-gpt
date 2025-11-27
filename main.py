import streamlit as st

from service.get_title import get_chat_title
from service.get_model_list import get_ollama_models_list
from service.chat_utlity import get_answer
from db.conversation import (
    create_new_conversation,
    add_message,
    get_conversation,
    get_all_conversation
)

st.set_page_config(
    page_title="Personal GPT",
    page_icon="💬",
    layout="centered"
)

st.title("🤖 Your Personal GPT")

if "OLLAMA_MODELS" not in st.session_state:
    st.session_state.OLLAMA_MODELS = get_ollama_models_list()

selected_model = st.selectbox("Select Model", st.session_state.OLLAMA_MODELS)

# session state
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("conversation_title", None)
st.session_state.setdefault("chat_history", [])     #({role, content})

# sidebar
with st.sidebar:
    st.header("💬 Chat History")
    conversations = get_all_conversation()

    if st.button("➕ New Chat"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = None
        st.session_state.chat_history = []

    for cid, title in conversations.items():
        is_current = cid == st.session_state.conversation_id
        label = f"{title}" if is_current else title
        if st.button(label, key=f"conv_{cid}"):
            doc = get_conversation(cid) or {}
            st.session_state.conversation_id = cid
            st.session_state.conversation_title = doc.get("title", "Untitled")
            st.session_state.chat_history = [
                {"role": m["role"], "content": m['content'] } for m in doc.get("messages", [])
            ]

# show chat so far
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# chat input
user_query = st.chat_input("ASK the GPT...")
if user_query:
    # show and store user msg in UI
    st.chat_message("user").markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # persist in db
    if st.session_state.conversation_id is None:
        try:
            title = get_chat_title(selected_model, user_query) or "New Chat"
        except Exception:
            title = "New Chat"
        conv_id = create_new_conversation(title=title, role="user", content=user_query)
        st.session_state.conversation_id = conv_id
        st.session_state.conversation_title = title
    else:
        add_message(st.session_state.conversation_id, "user", user_query)

    # get assistant response
    try:
        assistant_text = get_answer(selected_model, st.session_state.chat_history)
    except Exception as e:
        assistant_text = f"Error getting response: {e}"

    # show + store assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})

    # persist assistant message
    if st.session_state.conversation_id:
        add_message(st.session_state.conversation_id, "assistant", assistant_text or "Error: No response")