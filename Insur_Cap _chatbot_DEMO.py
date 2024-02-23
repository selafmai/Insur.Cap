import databutton as db
import streamlit as st
from openai import OpenAI

from key_check import check_for_openai_key

st.title("Insur.Cap 👀 ")

api_key = db.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.write(
    """
Redefining insurance. One image at a time.
"""
)

st.info(
    """
**The AI Assistant value proposition**
1. Take an image "snap"...
2. Model caption image and outline the potential perils and hazards.
3. Chatbot model NUDGE prevention behaviour that decrease risk.
"""
)

prompt_template = """
  You are a witty and helpful assistant that helps people use and 
  get started with an app template for image caption and deliver prevention instructions regarding the image caption. 
        
    The app starter template you are an assistant for, displays chatbot powered by a single
    prompt which happens to be identical to your instructions. 

    Always encourage people to go an play with the image caption. They can do that by snap and talking with chatbot AI assistant about the prevention behaviour. 
    The prompt is so long that there is no way they will miss it.
  
  
    Your job is to help people understand the image caption and to give the prevention nudge to decrease risk and avoid hazardus life style.
"""


# When calling ChatGPT, we  need to send the entire chat history together
# with the instructions. You see, ChatGPT doesn't know anything about
# your previous conversations so you need to supply that yourself.
# Since Streamlit re-runs the whole script all the time we need to load and
# store our past conversations in what they call session state.
prompt = st.session_state.get(
    "prompt", [{"role": "system", "content": prompt_template}]
)


# Here we display all messages so far in our convo
for message in prompt:
    # If we have a message history, let's display it
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])


# This is where the user types a question
question = st.chat_input("Ask me about the caption")
check_for_openai_key()

if question:  # Someone have asked a question
    # First we add the question to our message history
    prompt.append({"role": "user", "content": question})

    # Let's post our question and a place holder for the bot answer
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Here we call ChatGPT with streaming
    response = []
    result = ""
    for chunk in client.chat.completions.create(
        model="gpt-3.5-turbo", messages=prompt, stream=True
    ):
        text = chunk.choices[0].delta.content
        if text is not None:
            response.append(text)
            result = "".join(response).strip()

            # Let us update the Bot's answer with the new chunk
            botmsg.write(result)

    # When we get an answer back we add that to the message history
    prompt.append({"role": "assistant", "content": result})

    # Finally, we store it in the session state
    st.session_state["prompt"] = prompt
