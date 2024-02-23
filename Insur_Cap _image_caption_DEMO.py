# https://databutton.com/v/fn0hgnv6


import streamlit as st
import base64
import databutton as db
from openai import OpenAI
from key_check import check_for_openai_key

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(page_title="Image Analyst", layout="centered", initial_sidebar_state="collapsed")
# Streamlit page setup
st.title("  Insur.Cap 👀 ")
st.write("Redefining insurance. One image at a time.")


# Check if the OpenAI API key is set
check_for_openai_key()

# Retrieve the OpenAI API Key from secrets
api_key = db.secrets.get(name="OPENAI_API_KEY")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Display the uploaded image
if uploaded_file:
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)


# Prompt text ** IMPORTANT TO CUSTOMIZE TO YOUR OWN NEEDS **
# Example prompt 
prompt_text = ( '''
As an image analysis specialist, meticulously examine the provided image. 
Identify and describe the prominent features and patterns, using your expertise to deduce insights. 
Craft your explanation to be understandable to a non-specialist audience, yet detailed enough to reflect your specialist knowledge. 
Describe the image. Additionally, outline from image the caption objects and items with the attribute recognition. 
If there are OCR captions, also extract this data from the image.Outline the image description like a plain paragraph text with a few sentences.
Additional outline in bullets points the KEY ELEMENTS if there is present the: -[item] caption\n-[object] detection\n-[attribute] recognition\n-[image] segmentation\n-[OCR] text and number extraction\n-[adjective] semantic search\n-[subject] from the image\n-[doing action]\n-[mobility]\n-[transportation]\n-[person]\n-[animal]\n-[furniture]\n-[electronics]\n-[house appliances]\n-[landscape]\n-[environment]\n-[liability] context search\n  
Outline only the captioned KEY ELEMENTS categories as bullet points.
Finish with a bold caption that encapsulates your analysis in a brief statement.
'''
)

# Toggle for showing additional details input
show_details = st.toggle("Add details about the image", value=False, help = "More context about the image aids the model to be precise.")

# Additional details about the image, shown only if toggle is True
if show_details:
    additional_details = st.text_area(
        "Add any additional details or context about the image here:",
        disabled=not show_details, placeholder="Western Blot Anlaysis and fluorescence intensity of those result."
    )
    # APPENDING ADDITIONAL CONTEXT TO THE ALREADY GIVEN PROMPTS!
    if additional_details:
        prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"

# Button to trigger the analysis
analyze_button = st.button("Analyse the Image")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("📟 Analysing the image ..."):
        
        # Encode the image
        base64_image = encode_image(uploaded_file)
        st.markdown("-------")
        st.markdown("📟 Here's what I think about the image ...")
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]

        # Make the request to the OpenAI API
        try:
            # Stream the response back at the UI
            # Without Streaming the response is pretty slow
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages, 
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
