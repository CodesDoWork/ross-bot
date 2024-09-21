import os
import telebot
from dotenv import load_dotenv
from telebot.types import Message
from src.assistant import Assistant
from src.voice import VoiceRecognizer

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

assistant = Assistant()
voice_recognizer = VoiceRecognizer(bot)


@bot.message_handler(commands=["start", "hello", "init"])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, "Howdy, how are you doing?")


@bot.message_handler(func=lambda msg: True)
def handle_text(message: Message):
    process_request(message.chat.id, message.text)


@bot.message_handler(func=lambda msg: True, content_types=["voice"])
def handle_voice(message: Message):
    process_request(message.chat.id, voice_recognizer.recognize_speech(message.voice))


def process_request(chat_id: int, request: str):
    bot.send_message(chat_id, assistant.process_request(chat_id, request))


bot.infinity_polling()
