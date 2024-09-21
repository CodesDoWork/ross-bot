import os
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src.assistant import Assistant
from src.voice import VoiceRecognizer


LIKE = "like"
DISLIKE = "dislike"


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
            self.bot.send_message(chat_id, self.assistant.greet_user(chat_id, message.from_user))

        @self.bot.message_handler(func=lambda msg: True)
        def handle_text(message: Message):
            self.process_request(message.chat.id, message.text)

        @self.bot.message_handler(func=lambda msg: True, content_types=["voice"])
        def handle_voice(message: Message):
            self.process_request(message.chat.id, self.voice_recognizer.recognize_speech(message.voice))

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_feedback_buttons(call):
            self.bot.answer_callback_query(call.id)
            chat_id = call.message.chat.id
            self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
            if call.data == LIKE:
                self.bot.send_message(chat_id, self.assistant.positive_feedback(chat_id))
            elif call.data == DISLIKE:
                self.bot.send_message(chat_id, self.assistant.negative_feedback(chat_id))

    def process_request(self, chat_id: int, request: str):
        self.bot.send_message(chat_id, self.assistant.process_request(chat_id, request))

        if self.assistant.states[chat_id]["status"] == Assistant.Status.Feedback:
            self.ask_for_feedback(chat_id)

    def ask_for_feedback(self, chat_id: int):
        self.bot.send_message(chat_id, self.assistant.ask_for_feedback(chat_id), reply_markup=self.create_feedback_buttons())

    def create_feedback_buttons(self):
        markup = InlineKeyboardMarkup(row_width=2)
        thumbs_up = InlineKeyboardButton("👍", callback_data=LIKE)
        thumbs_down = InlineKeyboardButton("👎", callback_data=DISLIKE)
        markup.add(thumbs_up, thumbs_down)
        return markup

    def start(self):
        print("Bot is running...")
        self.bot.infinity_polling()
