import re
import os
from typing import Union

from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src.assistant import Assistant
from src.voice import VoiceRecognizer
from src.data import get_df


LIKE = "like"
DISLIKE = "dislike"
CHAT_PREFIX = "chat_"
EMAIL_PREFIX = "email_"
CALL_PREFIX = "call_"


class Bot:

    def __init__(self, domain: str, token: str = ""):
        self.bot = TeleBot(token or os.getenv("BOT_TOKEN"))
        self.setup_handlers()
        self.df = get_df()
        self.assistant = Assistant(self.df)
        self.voice_recognizer = VoiceRecognizer(self.bot)
        self.domain = domain

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
            self.process_request(message.chat.id, self.voice_recognizer.recognize_speech(message.voice, message.from_user))

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_feedback_buttons(call):
            self.bot.answer_callback_query(call.id)
            chat_id = call.message.chat.id
            if call.data == LIKE:
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, self.assistant.positive_feedback(chat_id))
            elif call.data == DISLIKE:
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, self.assistant.negative_feedback(chat_id))
            elif call.data.startswith(CHAT_PREFIX):
                self.bot.send_message(chat_id, "chat")
            elif call.data.startswith(EMAIL_PREFIX):
                self.bot.send_message(chat_id, "email")
            elif call.data.startswith(CALL_PREFIX):
                self.bot.send_message(chat_id, "call")

    def process_request(self, chat_id: int, request: str):
        response = self.assistant.process_request(chat_id, request)
        if self.is_contact_response(response):
            self.send_contacts(chat_id, response)
            self.assistant.set_feedback(chat_id)
            self.ask_for_feedback(chat_id)
        else:
            self.bot.send_message(chat_id, response)

    def ask_for_feedback(self, chat_id: int):
        self.bot.send_message(chat_id, self.assistant.ask_for_feedback(chat_id), reply_markup=self.create_feedback_buttons())

    def create_feedback_buttons(self):
        markup = InlineKeyboardMarkup(row_width=2)
        thumbs_up = InlineKeyboardButton("👍", callback_data=LIKE)
        thumbs_down = InlineKeyboardButton("👎", callback_data=DISLIKE)
        markup.add(thumbs_up, thumbs_down)
        return markup

    def get_emails(self, text: str) -> list[str]:
        return re.findall(fr"[\w.-_]+@{self.domain}", text)

    def is_contact_response(self, msg: str) -> bool:
        return len(self.get_emails(msg)) > 0

    def send_contacts(self, chat_id: int, msg: str):
        for email in self.get_emails(msg):
            print("Contact:", email)
            contact = self.df[self.df["email"].str.contains(email, case=False, na=False)]
            def field(field_name: str) -> str:
                return contact[field_name].values[0]

            markup = self.create_contact_markup(email)
            self.bot.send_message(chat_id, f"*{field('name')}*\n{field('position')} @ {field('department')}", reply_markup=markup, parse_mode="markdown")

    def create_contact_markup(self, email: str) -> Union[InlineKeyboardMarkup, None]:
        markup = InlineKeyboardMarkup(row_width=3)
        chat_action = InlineKeyboardButton("💬", callback_data=f"{CHAT_PREFIX}{email}")
        email_action = InlineKeyboardButton("✉", callback_data=f"{EMAIL_PREFIX}{email}")
        call_action = InlineKeyboardButton("📞", callback_data=f"{CALL_PREFIX}{email}")
        markup.add(chat_action, email_action, call_action)
        return markup

    def start(self):
        print("Bot is running...")
        self.bot.infinity_polling()
