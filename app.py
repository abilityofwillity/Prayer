from gtts import gTTS
import streamlit as st
from pydub import AudioSegment
import whisper
import tempfile
import os

st.set_page_config(page_title="Prayer Personalizer", layout="centered")
st.title("🙏 Prayer Personalizer")
st.write("Replace the name 'Tim' in this prayer with a name of your choice.")

name_input = st.text_input("Enter the name to replace 'Tim' with:")

if st.button("Generate Personalized Prayer"):
    if not name_input.strip():
        st.warning("Please enter a name.")
    else:
        with st.spinner("Transcribing audio..."):
            model = whisper.load_model("base")
            result = model.transcribe("prayer_original.wav", word_timestamps=True)

        name_times = [
            (word["start"], word["end"])
            for segment in result["segments"]
            for word in segment.get("words", [])
            if word["word"].strip().lower() == "tim"
        ]

        if not name_times:
            st.error("No occurrences of 'Tim' found.")
            st.stop()

        with st.spinner("Generating name audio using gTTS..."):
            tts = gTTS(text=name_input)
            tts_path = f"temp_{name_input}.mp3"
            tts.save(tts_path)
            name_audio = AudioSegment.from_file(tts_path)

        with st.spinner("Replacing segments..."):
            original = AudioSegment.from_wav("prayer_original.wav")
            output = AudioSegment.empty()
            cursor = 0

            for start, end in name_times:
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                output += original[cursor:start_ms]
                output += name_audio
                cursor = end_ms

            output += original[cursor:]
            final_path = f"personalized_prayer_{name_input}.wav"
            output.export(final_path, format="wav")

        with open(final_path, "rb") as f:
            audio_bytes = f.read()
            st.success("✅ Personalized prayer ready!")
            st.audio(audio_bytes, format="audio/wav")
            st.download_button("Download", data=audio_bytes, file_name=final_path)

        os.remove(tts_path)
        os.remove(final_path)


