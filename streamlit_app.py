import io
import os
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
from config import get_api_key

st.set_page_config(
    page_title="AI Voice Assistant & Chatbot",
    page_icon="🎙️",
    layout="centered"
)

# ----------------- Custom Styling -----------------
st.markdown("""
<style>
    .stAppHeader {background-color: transparent;}
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .badge {
        background-color: #E0E7FF;
        color: #4338CA;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎙️ AI Voice Assistant & Chatbot</div>', unsafe_allow_html=True)
st.markdown('<span class="badge">Powered by Google Gemini</span>', unsafe_allow_html=True)

# ----------------- Sidebar Configuration -----------------
st.sidebar.title("⚙️ Settings")

api_key = get_api_key()

if not api_key:
    st.sidebar.warning("⚠️ Gemini API Key not detected!")
    user_key = st.sidebar.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Get a free key from Google AI Studio (aistudio.google.com)"
    )
    if user_key:
        st.session_state.user_api_key = user_key
        api_key = user_key
        st.rerun()

model_name = st.sidebar.selectbox(
    "Select AI Model",
    [
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-pro-latest",
        "gemini-1.5-flash"
    ],
    help="gemini-flash-latest is fast and recommended for voice responses."
)

enable_tts = st.sidebar.checkbox("🔊 Voice Responses (Text-to-Speech)", value=True)

tts_lang = st.sidebar.selectbox(
    "Voice Language",
    ["en", "hi", "es", "fr", "de"],
    format_func=lambda x: {"en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German"}.get(x, x)
)

temperature = st.sidebar.slider(
    "Temperature (Creativity)",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1
)

max_tokens = st.sidebar.slider(
    "Maximum Output Tokens",
    min_value=100,
    max_value=2048,
    value=512,
    step=100
)

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# ----------------- Client Initialization -----------------
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as err:
        st.sidebar.error(f"Error initializing client: {err}")

# ----------------- Session State -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- Audio Helper Function -----------------
def generate_tts_audio(text: str, lang: str = "en") -> bytes:
    try:
        # Limit text size for fast audio synthesis
        clean_text = text[:1000] if len(text) > 1000 else text
        tts = gTTS(text=clean_text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"Audio generation failed: {e}")
        return None

# ----------------- Display Previous Messages -----------------
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message and message["audio"]:
            st.audio(message["audio"], format="audio/mp3")

# ----------------- Check API Key -----------------
if not api_key:
    st.info("💡 Please enter your Gemini API Key in the sidebar or set `GEMINI_API_KEY` in your environment / Streamlit Secrets to start.")
    st.stop()

# ----------------- User Inputs (Audio & Text) -----------------
st.subheader("🎙️ Voice Input")
audio_val = st.audio_input("Record your voice prompt:")

prompt = st.chat_input("Or type your message here...")

user_prompt = None
audio_bytes = None

if audio_val is not None:
    # Read audio input
    audio_bytes = audio_val.read()
    if audio_bytes and len(audio_bytes) > 0:
        user_prompt = "🎤 [Voice Input Recorded]"

if prompt:
    user_prompt = prompt

if user_prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if audio_bytes:
                    # Multimodal audio input to Gemini
                    audio_part = types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    )
                    prompt_instructions = "Please listen to this audio clip and answer the user's request clearly and concisely."
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[audio_part, prompt_instructions],
                        config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens
                        }
                    )
                else:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens
                        }
                    )

                answer_text = response.text or "I couldn't generate a text response."
                st.markdown(answer_text)

                audio_output = None
                if enable_tts and answer_text:
                    audio_output = generate_tts_audio(answer_text, lang=tts_lang)
                    if audio_output:
                        st.audio(audio_output, format="audio/mp3", autoplay=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "audio": audio_output
                })

            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    st.error("⚠️ Gemini API quota exceeded or rate limited. Please try again in a few moments or switch model.")
                elif "404" in err_msg or "NOT_FOUND" in err_msg:
                    st.error(f"⚠️ Model '{model_name}' was not found or is unavailable. Please select another model from the sidebar.")
                else:
                    st.error(f"⚠️ Error generating content: {err_msg}")

# ----------------- Download Chat History -----------------
if st.session_state.messages:
    chat_text = ""
    for msg in st.session_state.messages:
        chat_text += f"{msg['role'].upper()}:\n{msg['content']}\n\n"
    
    st.sidebar.download_button(
        label="📥 Download Chat History",
        data=chat_text,
        file_name="voice_chat_history.txt",
        mime="text/plain"
    )
