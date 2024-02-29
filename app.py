import streamlit as st
from PIL import Image

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai.client.model import Model
import io
import base64

PAT = 'a90021e0adb7490c95e36f65f6d0974d'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'openai'
APP_ID = 'chat-completion'
# Change these to whatever model and text URL you want to use
MODEL_ID = 'gpt-4-vision-alternative'
MODEL_VERSION_ID = '12b67ac2b5894fb9af9c06ebf8dc02fb'


channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)


def get_image_details(prompt, image=None):
   

    # image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

    openai_api_key = PAT

    inference_params = dict(temperature=0.2, max_tokens=200, image_base64=image)

    # Model Predict
    model_prediction = Model("https://clarifai.com/openai/chat-completion/models/gpt-4-vision").predict_by_bytes(prompt.encode(), input_type="text", inference_params=inference_params)
    data = model_prediction.outputs[0].data.text.raw
    
    return data

def get_chat_response(text):
    if text is None:
        return
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        text=resources_pb2.Text(
                            raw=text
                            # url=TEXT_FILE_URL
                            # raw=file_bytes
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

    output = post_model_outputs_response.outputs[0]
    
    return output.data.text.raw

    

def main():
    st.set_page_config(layout="wide")  # Set the entire page to wide layout

    option = st.sidebar.selectbox("Choose an option", ["Upload Image"])
    chat_enable = True
    img_prompt = """As an image analysis specialist, meticulously examine the provided image. 
                Identify and describe the prominent features and patterns, using your expertise to deduce insights. 
                Craft your explanation to be understandable to a non-specialist audience, yet detailed enough to reflect your specialist knowledge. 
                Describe the image. Additionally, outline from image the caption objects and items with the attribute recognition. 
                If there are OCR captions, also extract this data from the image.Outline the image description like a plain paragraph text with a few sentences.
                Additional outline in bullets points the KEY ELEMENTS if there is present the: -[item] caption\n-[object] detection\n-[attribute] recognition\n-[image] segmentation\n-[OCR] text and number extraction\n-[adjective] semantic search\n-[subject] from the image\n-[doing action]\n-[mobility]\n-[transportation]\n-[person]\n-[animal]\n-[furniture]\n-[electronics]\n-[house appliances]\n-[landscape]\n-[environment]\n-[liability] context search\n  
                Outline only the captioned KEY ELEMENTS categories as bullet points.
                Finish with a bold caption that encapsulates your analysis in a brief statement."""
    # Set the width of the entire page
    

    # Divide the page into two columns
    col1, col2 = st.columns([1, 2])  # Adjust the relative widths as needed
    base64_image = None

    
    with col1:
        st.header("Upload an Image")

    if option == "Upload Image":
        with col1:
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                chat_enable = False
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                image_bytes = io.BytesIO()
                image.save(image_bytes,format=image.format)
                image_bytes = image_bytes.getvalue()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                captions = get_image_details(img_prompt, base64_image)
                st.write(captions)
                
            
                
            
        with col2:
            
            if "messages" not in st.session_state.keys(): # Initialize the chat message history
                st.session_state.messages = [
                    {"role": "assistant", "content": "Ask me a question about Insurance. I am here to help you."}
                ]  
            if prompt := st.chat_input(placeholder="Your question", disabled=chat_enable): # Prompt for user input and save to chat history
                response = get_image_details(prompt, base64_image)
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": response})
            with st.container(height=654):
                for message in st.session_state.messages: # Display the prior chat messages
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                    
if __name__ == "__main__":
    main()
