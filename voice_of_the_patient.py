import os
import logging
from io import BytesIO
from pydub import AudioSegment
import speech_recognition as sr

# Optional: playback libraries
import platform
import subprocess

# ElevenLabs TTS
from elevenlabs import ElevenLabs, save

# Groq STT
from groq import Groq

# ---------------------------
# CONFIG
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

audio_filepath = "patient_voice_test_for_patient.mp3"
tts_output_filepath = "doctor_voice_response.mp3"

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("❌ ELEVENLABS_API_KEY not set in environment variables.")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not set in environment variables.")

# ---------------------------
# RECORD AUDIO FUNCTION
# ---------------------------
def record_audio(file_path, timeout=20, phrase_time_limit=None):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            # Save as MP3
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Audio saved to {file_path}")
    except Exception as e:
        logging.error(f"Error recording audio: {e}")

# ---------------------------
# TRANSCRIBE AUDIO FUNCTION
# ---------------------------
def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    if not os.path.isfile(audio_filepath):
        raise FileNotFoundError(f"Audio file not found: {audio_filepath}")
    
    client = Groq(api_key=GROQ_API_KEY)
    with open(audio_filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=stt_model,
            file=audio_file,
            language="en"
        )
    return transcription.text

# ---------------------------
# ELEVENLABS TTS FUNCTION
# ---------------------------
def text_to_speech_with_elevenlabs(input_text, output_filepath, voice_name="Rachel"):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    # Using the latest ElevenLabs SDK interface
    audio = client.studio.text_to_speech(
        voice=voice_name,
        text=input_text,
        model="eleven_turbo_v2",
        output_format="mp3_22050_32"
    )
    save(audio, output_filepath)
    logging.info(f"✅ ElevenLabs Audio saved as {output_filepath}")

# ---------------------------
# AUDIO PLAYBACK FUNCTION
# ---------------------------
def play_audio(file_path):
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', file_path])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{file_path}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', file_path])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        logging.error(f"Error playing audio: {e}")

# ---------------------------
# MAIN PIPELINE
# ---------------------------
if __name__ == "__main__":
    # Step 1: Record audio from user
    record_audio(audio_filepath)
    
    # Step 2: Transcribe audio
    transcription_text = transcribe_with_groq(
        stt_model="whisper-large-v3",
        audio_filepath=audio_filepath,
        GROQ_API_KEY=GROQ_API_KEY
    )
    logging.info(f"Transcribed Text: {transcription_text}")
    
    # Step 3: Convert transcription to TTS
    text_to_speech_with_elevenlabs(
        input_text=transcription_text,
        output_filepath=tts_output_filepath,
        voice_name="Aria"  # you can change voice here
    )
    
    # Step 4: Play the generated speech
    play_audio(tts_output_filepath)
