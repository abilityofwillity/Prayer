import streamlit as st
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="🙏 Prayer Personalizer", layout="centered")
st.title("🙏 Prayer Personalizer")

st.write("This app replaces the name **'Tim'** in the prayer with a name of your choice.")

name = st.text_input("Enter the name to personalize:")

if st.button("Generate Personalized Prayer") and name.strip():
    with st.spinner("Creating prayer..."):
        # Base message with [NAME] placeholder
        base_text = (
            "Dear Lord, please bless Tim with strength and guidance. "
            "Walk beside Tim every day, giving peace to Tim’s heart. "
            "We ask You to lift Tim up in Your love, Lord. Amen."
        )

        personalized_text = base_text.replace("Tim", name)

        # Use gTTS to synthesize the personalized audio
        tts = gTTS(text=personalized_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            audio_file_path = tmp.name

    # Load and offer playback + download
    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    st.success("✅ Prayer ready!")
    st.audio(audio_bytes, format="audio/mp3")
    st.download_button("Download Prayer", audio_bytes, file_name=f"prayer_for_{name}.mp3")

    os.remove(audio_file_path)



