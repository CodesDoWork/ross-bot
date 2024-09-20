import os
import tempfile

from dotenv import load_dotenv
import telebot
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI()
recognizer = sr.Recognizer()


@bot.message_handler(commands=["start", "hello", "init"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Howdy, how are you doing?")


@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    process_request(message.chat.id, message.text)


@bot.message_handler(func=lambda msg: True, content_types=["voice"])
def handle_voice(message):
    process_request(message.chat.id, recognize_speech(message.voice))


def process_request(chat_id: int, request: str):
    bot.send_message(chat_id, request)


def recognize_speech(voice) -> str:
    """Processes voice messages, transcribes them, and sends the transcription to the chat."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
        file_path = temp_voice_file.name
        wav_file_path = file_path.replace(".ogg", ".wav")

    file_info = bot.get_file(voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    ogg_audio = AudioSegment.from_ogg(file_path)
    ogg_audio.export(wav_file_path, format="wav")
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language='de-DE')
        return text
    except sr.UnknownValueError:
        return "Entschuldigung, ich kann dich nicht verstehen."
    except sr.RequestError as e:
        print(f"Fehler bei der Spracherkennung: {e}")
        return "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
    finally:
        os.remove(file_path)
        os.remove(wav_file_path)


def gpt(request: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": request
            }
        ]
    )

    return completion.choices[0].message.content


bot.infinity_polling()
