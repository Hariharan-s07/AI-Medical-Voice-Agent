import os
import platform
import subprocess
from gtts import gTTS
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment  # pip install pydub

# ==========================
# CONFIG
# ==========================
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ==========================
# Utility: Convert mp3 → wav
# ==========================
def convert_to_wav(mp3_file, wav_file):
    sound = AudioSegment.from_mp3(mp3_file)
    sound.export(wav_file, format="wav")
    return wav_file

# ==========================
# Cross-OS Player
# ==========================
def play_audio(file_path):
    os_name = platform.system()
    try:
        if os_name == "Windows":
            # Windows SoundPlayer needs WAV
            if file_path.endswith(".mp3"):
                wav_file = file_path.replace(".mp3", ".wav")
                file_path = convert_to_wav(file_path, wav_file)
            subprocess.run(['powershell', '-c',
                           f'(New-Object Media.SoundPlayer "{file_path}").PlaySync();'])
        elif os_name == "Darwin":  # macOS
            subprocess.run(['afplay', file_path])
        elif os_name == "Linux":
            subprocess.run(['aplay', file_path])
        else:
            raise OSError("Unsupported OS")
    except Exception as e:
        print(f"[ERROR] Could not play audio: {e}")

# ==========================
# ElevenLabs v2
# ==========================
def text_to_speech_with_elevenlabs(input_text, output_filepath, voice_id="21m00Tcm4TlvDq8ikWAM"):
    try:
        audio = client.text_to_speech.convert(
            model_id="eleven_turbo_v2",
            voice_id=voice_id,
            text=input_text,
            output_format="mp3_22050_32"
        )
        save(audio, output_filepath)
        print(f"[ElevenLabs v2] Saved: {output_filepath}")
        play_audio(output_filepath)
    except Exception as e:
        print(f"[ERROR] ElevenLabs v2 failed: {e}")

# ==========================
# gTTS
# ==========================
def text_to_speech_with_gtts(input_text, output_filepath):
    try:
        tts = gTTS(text=input_text, lang="en", slow=False)
        tts.save(output_filepath)
        print(f"[gTTS] Saved: {output_filepath}")
        play_audio(output_filepath)
    except Exception as e:
        print(f"[ERROR] gTTS failed: {e}")

# ==========================
# TEST
# ==========================
if __name__ == "__main__":
    text = "Hello, this is AI Hassan, testing ElevenLabs and Google TTS with autoplay on Windows!"

    text_to_speech_with_elevenlabs(text, "elevenlabs_testing_v2.mp3")
    text_to_speech_with_gtts(text, "gtts_testing.mp3")
