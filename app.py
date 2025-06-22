import streamlit as st
from pydub import AudioSegment
from TTS.api import TTS
import whisper
import tempfile
import os

# Set Streamlit config
st.set_page_config(page_title="Prayer Personalizer", layout="centered")
st.title("🙏 Prayer Personalizer")
st.write("Replace the name 'Tim' in the original prayer with any name you choose.")

# Name input
name_input = st.text_input("Enter the name to replace 'Tim' with:")

if st.button("Generate Personalized Prayer"):
    if not name_input.strip():
        st.warning("Please enter a valid name.")
    else:
        # Transcribe audio
        with st.spinner("Transcribing original prayer..."):
            model = whisper.load_model("base")
            result = model.transcribe("prayer_original.wav", word_timestamps=True)

        # Find timestamps for the word "Tim"
        name_times = [
            (word["start"], word["end"])
            for segment in result["segments"]
            for word in segment.get("words", [])
            if word["word"].strip().lower() == "tim"
        ]

        if not name_times:
            st.error("Could not find the name 'Tim' in the prayer.")
            st.stop()

        # Generate replacement name audio
        with st.spinner("Generating new audio for the name..."):
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tts.tts_to_file(name_input, tmp.name)
                replacement_audio = AudioSegment.from_wav(tmp.name)
            os.remove(tmp.name)

        # Load original and build new audio
        with st.spinner("Rebuilding the prayer..."):
            original_audio = AudioSegment.from_wav("prayer_original.wav")
            output = AudioSegment.empty()
            cursor = 0

            for start, end in name_times:
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                output += original_audio[cursor:start_ms]
                output += replacement_audio
                cursor = end_ms

            output += original_audio[cursor:]

            output_path = f"personalized_prayer_{name_input}.wav"
            output.export(output_path, format="wav")

        # Offer playback and download
        with open(output_path, "rb") as f:
            audio_bytes = f.read()
            st.success("✅ Prayer ready!")
            st.audio(audio_bytes, format="audio/wav")
            st.download_button("Download Personalized Prayer", data=audio_bytes, file_name=output_path)

        os.remove(output_path)

