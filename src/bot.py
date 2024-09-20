import os
from dotenv import load_dotenv
import telebot
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import openai
from pydub import AudioSegment
import tempfile
import asyncio

# Load environment variables (tokens)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debugging token load
print(f"Loaded BOT_TOKEN: {BOT_TOKEN}")  # Check if the token is loaded
if BOT_TOKEN is None:
    raise Exception("Bot token is not defined! Check your .env file.")

bot = telebot.TeleBot(BOT_TOKEN)

# Set the FFmpeg path dynamically based on the location of the Python script
script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(script_dir, 'bin', 'ffmpeg.exe')
print(ffmpeg_path)
ffprobe_path = os.path.join(script_dir, 'bin', 'ffprobe.exe')
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Initialize speech recognizer
recognizer = sr.Recognizer()

# OpenAI setup
def setup_openai():
    openai.api_key = OPENAI_API_KEY

# Function to transcribe voice message using speech recognition
def transcribe_voice(voice_file_path):
    wav_file_path = convert_ogg_to_wav(voice_file_path)
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='de-DE')
            return text
        except sr.UnknownValueError:
            return "Entschuldigung, ich konnte dich nicht verstehen."
        except sr.RequestError as e:
            return f"Fehler bei der Spracherkennung: {e}"

# Convert OGG audio to WAV using pydub
def convert_ogg_to_wav(ogg_path):
    try:
        audio = AudioSegment.from_ogg(ogg_path)
        wav_file_path = tempfile.mktemp(suffix=".wav")
        audio.export(wav_file_path, format="wav")
        return wav_file_path
    except Exception as e:
        return f"Fehler bei der Audiokonvertierung: {e}"

# Function to generate a response using GPT
async def gpt_process(text):
    try:
        response = await asyncio.to_thread(openai.ChatCompletion.create,
                                           model="gpt-3.5-turbo",  
                                           messages=[
                                               {"role": "system", "content": "You are a helpful assistant."},
                                               {"role": "user", "content": text}
                                           ],
                                           max_tokens=150,
                                           n=1)
        gpt_text = response.choices[0].message['content'].strip()
        return gpt_text
    except Exception as e:
        return f"Fehler bei der GPT-Verarbeitung: {e}"

# Handle start command
@bot.message_handler(commands=["start", "hello", "init"])
def send_welcome(message):
    bot.reply_to(message, "Willkommen! Schick mir eine Nachricht oder eine Sprachnachricht.")

# Handle voice messages
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    voice_file = bot.download_file(file_info.file_path)
    
    # Save the voice message temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
        temp_voice_file.write(voice_file)
        voice_path = temp_voice_file.name

    try:
        # Transcribe the voice message
        transcribed_text = transcribe_voice(voice_path)

        # Respond with transcribed text
        bot.reply_to(message, f'Transkribierter Text: {transcribed_text}')

        # Process transcribed text with GPT
        gpt_reply = asyncio.run(gpt_process(transcribed_text))
        bot.reply_to(message, f'GPT Antwort: {gpt_reply}')

    except Exception as e:
        bot.reply_to(message, f"Fehler bei der Verarbeitung der Sprachnachricht: {e}")

    finally:
        # Clean up temporary files
        if os.path.exists(voice_path):
            os.remove(voice_path)

# Handle text messages
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    user_text = message.text
    
    # Process text using GPT
    gpt_reply = asyncio.run(gpt_process(user_text))
    
    # Reply with GPT response
    bot.reply_to(message, f'GPT Antwort: {gpt_reply}')

# Main bot polling loop
if __name__ == '__main__':
    setup_openai()
    bot.infinity_polling()
