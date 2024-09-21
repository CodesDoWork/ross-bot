import os
from telebot import TeleBot
from telebot.types import Message
from src.assistant import Assistant
from src.voice import VoiceRecognizer


class Bot:

    def __init__(self, token: str = ""):
        self.bot = TeleBot(token or os.getenv("BOT_TOKEN"))
        self.setup_handlers()
        self.assistant = Assistant()
        self.voice_recognizer = VoiceRecognizer(self.bot)

    def setup_handlers(self):
        @self.bot.message_handler(commands=["start", "hello", "init"])
        def send_welcome(message: Message):
            chat_id = message.chat.id
            self.bot.send_message(chat_id, "Howdy, how are you doing?")

        @self.bot.message_handler(func=lambda msg: True)
        def handle_text(message: Message):
            self.process_request(message.chat.id, message.text)

        @self.bot.message_handler(func=lambda msg: True, content_types=["voice"])
        def handle_voice(message: Message):
            self.process_request(message.chat.id, self.voice_recognizer.recognize_speech(message.voice))

    def process_request(self, chat_id: int, request: str):
        self.bot.send_message(chat_id, self.assistant.process_request(chat_id, request))

    def start(self):
        print("Bot is running...")
        self.bot.infinity_polling()
