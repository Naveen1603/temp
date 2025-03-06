import streamlit as st
import requests

API_URL = "YOUR_API_ENDPOINT"  # Replace with your actual API URL

st.title("CORE Document Narration")

text_input = st.text_area("Enter Text", placeholder="Type something to generate audio...")

# Toggle for male/female audio
male_audio = st.toggle("Use Male Voice", value=True)

if st.button("Generate"):
    if text_input.strip():
        payload = {"text": text_input, "male_audio": male_audio}
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            qr_path = data.get("qr_path")
            audio_link = data.get("audio_link")

            if qr_path:
                st.image(qr_path, caption="QR Code")
            if audio_link:
                st.markdown(f"[Click to listen]({audio_link})", unsafe_allow_html=True)
        else:
            st.error("Error generating audio.")
    else:
        st.warning("Please enter text to generate audio.")
