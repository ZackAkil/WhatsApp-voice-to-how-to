import streamlit as st
import io
from google.cloud import speech

# Set page title
st.title("Physio Voice-2-Plan")
st.subheader("(WhatsApp voice file)")


if 'physio_transcript' not in st.session_state:
    st.session_state.physio_transcript = ''

if 'physio_plan' not in st.session_state:
    st.session_state.physio_plan = ''

# Function to transcribe the audio
def transcribe_audio(audio_data):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_data)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz= 16000,
        enable_automatic_punctuation=True,

        language_code="en-GB"  # Adjust language code if needed
    )

    response = client.recognize(config=config, audio=audio)

    print(response)
    # Extract the transcribed text 
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript + " "

    return transcription


def create_pysio_plan(text):
    from gemini import generate_pysio_plan
    return generate_pysio_plan(text)

# File uploader component
uploaded_file = st.file_uploader("Upload an audio file", type=["opus"])

if uploaded_file is not None:
    # Read audio data
    audio_data = uploaded_file.read()
    st.audio(audio_data, format='audio/opus')

    # Display transcription button
    if st.button("Transcribe"):
        try:
            transcription = transcribe_audio(audio_data)
            st.session_state.physio_transcript = transcription
            st.success("Transcription:")
        except Exception as e:
            print(e)
            st.error(e)
            st.error("An error occurred during transcription. Please try again.")

if st.session_state.physio_transcript:
    transcription = st.session_state.physio_transcript
    st.write(transcription)

    if st.button('Convert to plan'):

        with st.spinner('Generating plan...'):
            st.session_state.physio_plan = create_pysio_plan(transcription)

if st.session_state.physio_plan:
    with st.container(border=True):
        st.markdown(st.session_state.physio_plan)
