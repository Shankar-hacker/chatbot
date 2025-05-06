import streamlit as st
import time
import openai
from openai import OpenAI

# Helper function to safely render markdown
def safe_markdown(text):
    try:
        st.markdown(text)
    except UnicodeEncodeError:
        st.markdown(text.encode('utf-8', 'ignore').decode())

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            safe_markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            safe_markdown(prompt)

        # Attempt to generate a response using the OpenAI API.
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response and store it.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
                safe_markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except openai.RateLimitError:
            st.error("Rate limit reached. Please wait and try again shortly.", icon="⏳")
        except openai.OpenAIError as e:
            st.error(f"An error occurred: {e}", icon="⚠️")
        except UnicodeEncodeError:
            st.error("A Unicode encoding error occurred. Some characters may not display correctly.", icon="🔤")