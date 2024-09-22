import re
import os

from telebot import TeleBot  
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton  

from src.assistant import Assistant
from src.voice import VoiceRecognizer
from src.data import get_df

# Constants used to handle feedback and contact actions
LIKE = "like"  # Feedback constant for positive feedback
DISLIKE = "dislike"  # Feedback constant for negative feedback
CHAT_PREFIX = "chat_"  # Prefix for chat-related interactions
EMAIL_PREFIX = "email_"  # Prefix for email-related interactions
CALL_PREFIX = "call_"  # Prefix for phone-call-related interactions


class Bot:
    """Main class for managing the bot's operations."""

    def __init__(self, domain: str, token: str = ""):
        """
        Initializes the bot with a domain (for filtering email contacts) and a teelegram token for authentication.

        :param domain: The email domain for filtering contacts.
        :param token: Optional; the bot token, fetched from the environment `BOT_TOKEN` if not provided.
        """
        self.bot = TeleBot(token or os.getenv("BOT_TOKEN"))

        self.setup_handlers()

        self.df = get_df()
        self.assistant = Assistant(self.df)
        self.voice_recognizer = VoiceRecognizer(self.bot)
        self.domain = domain

    def setup_handlers(self):
        """
        Defines and registers the bot's message and callback query handlers.
        """
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

    def process_request(self, chat_id: int, request: str):
        """
        Processes incoming text requests. Checks if the request results in a contact lookup and sends appropriate responses.

        :param chat_id: ID of the chat where the request came from.
        :param request: The user's message or recognized speech.
        """
        response = self.assistant.process_request(chat_id, request)
        if self.is_contact_response(response):
            self.send_contacts(chat_id, response)
            self.assistant.set_feedback(chat_id)
            self.ask_for_feedback(chat_id)
        else:
            self.bot.send_message(chat_id, response)

    def ask_for_feedback(self, chat_id: int):
        """
        Asks the user for feedback (like/dislike) after providing a response.

        :param chat_id: ID of the chat where feedback is requested.
        """
        self.bot.send_message(chat_id, self.assistant.ask_for_feedback(chat_id), reply_markup=self.create_feedback_buttons())

    def create_feedback_buttons(self) -> InlineKeyboardMarkup:
        """
        Creates a feedback keyboard with 'like' and 'dislike' buttons.

        :return: InlineKeyboardMarkup with thumbs up and down buttons.
        """
        markup = InlineKeyboardMarkup(row_width=2)  # Two buttons in a row.
        thumbs_up = InlineKeyboardButton("👍", callback_data=LIKE)
        thumbs_down = InlineKeyboardButton("👎", callback_data=DISLIKE)
        markup.add(thumbs_up, thumbs_down)
        return markup

    def get_emails(self, text: str) -> list[str]:
        """
        Extracts email addresses from a given text that match the specified domain.

        :param text: Input text to search for email addresses.
        :return: A list of email addresses found in the text.
        """
        return re.findall(fr"[\w._-]+@{self.domain}", text)

    def is_contact_response(self, msg: str) -> bool:
        """
        Checks if a response contains email addresses (indicating contact information).

        :param msg: The message to search for email addresses.
        :return: True if the message contains email addresses, otherwise False.
        """
        return len(self.get_emails(msg)) > 0

    def send_contacts(self, chat_id: int, msg: str):
        """
        Sends contact information based on emails found in the message.

        :param chat_id: ID of the chat where contact info is sent.
        :param msg: The message containing contact information.
        """
        for email in self.get_emails(msg):
            contact = self.df[self.df["email"].str.contains(email, case=False, na=False)]
            
            def field(field_name: str) -> str:
                return contact[field_name].values[0]

            markup = self.create_contact_markup(email)
            self.bot.send_message(chat_id, f"*{field('name')}*\n{field('position')} @ {field('department')}", reply_markup=markup, parse_mode="markdown")

    def create_contact_markup(self, email: str) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with contact actions (chat, email, call).

        :param email: The email of the contact.
        :return: InlineKeyboardMarkup with buttons for chat, email, and call.
        """
        contact = self.df[self.df["email"].str.contains(email, case=False, na=False)]
        phone_number = contact["phone"].values[0]

        telegram_url = f"https://t.me/AICentaurBot"  # Telegram deep link (placeholder).
        email_url = f"https://ai-hackathon-2024-redirect.j-konratt.workers.dev?email={email}"
        tel_url = f"https://ai-hackathon-2024-redirect.j-konratt.workers.dev?tel={phone_number}"

        markup = InlineKeyboardMarkup(row_width=3)
        chat_action = InlineKeyboardButton("💬", url=telegram_url)
        email_action = InlineKeyboardButton("✉", url=email_url)
        tel_action = InlineKeyboardButton("📞", url=tel_url)

        markup.add(chat_action, email_action, tel_action)
        return markup

    def start(self):
        """
        Starts the bot's event loop, waiting for messages and handling interactions indefinitely.
        """
        print("Bot is running...")
        self.bot.infinity_polling()
