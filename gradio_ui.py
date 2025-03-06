import gradio as gr
import requests

API_URL = "YOUR_API_ENDPOINT"  # Replace with your actual API URL

def generate_audio(text):
    payload = {"text": text, "male_audio": True}
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        qr_path = data.get("qr_path")
        audio_link = data.get("audio_link")
        return qr_path, audio_link
    else:
        return None, "Error generating audio."

with gr.Blocks() as app:
    gr.Markdown("## CORE Document Narration")

    with gr.Row():
        text_input = gr.Textbox(label="Enter Text", placeholder="Type something to generate audio...")
        generate_btn = gr.Button("Generate")

    qr_output = gr.Image(label="QR Code")
    audio_output = gr.Markdown()

    def update_output(text):
        qr, audio = generate_audio(text)
        return qr, f"[Click to listen]({audio})" if audio else "Failed to generate audio."

    generate_btn.click(update_output, inputs=[text_input], outputs=[qr_output, audio_output])

app.launch()
