"""
This script implements a Telegram bot using the TeleBot library. The bot provides several functionalities, including:
1. Responding to commands and text messages.
2. Processing voice messages via a voice recognition system.
3. Identifying and sending contact information based on user requests, such as email addresses.
4. Allowing users to interact with the bot through inline buttons for feedback (like/dislike).
5. Presenting options for chatting, emailing, or calling contacts through custom keyboard actions.

The bot uses the `Assistant` class to handle responses and the `VoiceRecognizer` class to process speech. It retrieves contact information from a dataframe and provides the user with buttons for interacting with specific contacts (e.g., starting a Telegram chat, sending an email, or making a phone call).
"""

import re  # Regular expressions for pattern matching, especially for extracting emails from text.
import os  # For accessing environment variables, such as the bot token.

# Importing necessary modules from the Telebot library for bot creation and interaction
from telebot import TeleBot  
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton  

# Importing custom classes from the src directory for assisting with bot tasks
from src.assistant import Assistant  # Handles assistant-related tasks (like greeting users, processing requests).
from src.voice import VoiceRecognizer  # Manages voice recognition features for the bot.
from src.data import get_df  # Loads the dataframe containing the contact information.

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
        Initializes the bot with a domain (for filtering email contacts) and a token for authentication.

        :param domain: The email domain for filtering contacts.
        :param token: Optional; the bot token, fetched from the environment if not provided.
        """
        # Create a TeleBot instance. If a token isn't provided, fetch it from the environment variables.
        self.bot = TeleBot(token or os.getenv("BOT_TOKEN"))

        # Set up handlers for different message and callback events.
        self.setup_handlers()

        # Load contact data from the dataframe and initialize assistant and voice recognizer.
        self.df = get_df()
        self.assistant = Assistant(self.df)  # Assistant to help process user requests.
        self.voice_recognizer = VoiceRecognizer(self.bot)  # Voice recognizer for handling voice messages.
        self.domain = domain  # Email domain to match contacts.

    def setup_handlers(self):
        """
        Defines and registers the bot's message and callback query handlers.
        """
        # Handler for start/init commands. Sends a welcome message when "/start", "/hello", or "/init" commands are received.
        @self.bot.message_handler(commands=["start", "hello", "init"])
        def send_welcome(message: Message):
            chat_id = message.chat.id
            # Sends a personalized greeting to the user based on their Telegram ID.
            self.bot.send_message(chat_id, self.assistant.greet_user(chat_id, message.from_user))

        # Handler for any text message. This is a catch-all handler that processes any incoming text.
        @self.bot.message_handler(func=lambda msg: True)
        def handle_text(message: Message):
            self.process_request(message.chat.id, message.text)

        # Handler for voice messages. It captures the audio, converts it to text, and processes the request.
        @self.bot.message_handler(func=lambda msg: True, content_types=["voice"])
        def handle_voice(message: Message):
            # Recognizes the voice message and processes it as a text request.
            self.process_request(message.chat.id, self.voice_recognizer.recognize_speech(message.voice, message.from_user))

        # Handler for button clicks (like/dislike feedback). Handles the feedback from the user.
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_feedback_buttons(call):
            self.bot.answer_callback_query(call.id)  # Acknowledge the button click.
            chat_id = call.message.chat.id
            if call.data == LIKE:
                # Removes the markup (buttons) after the user provides positive feedback.
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, self.assistant.positive_feedback(chat_id))
            elif call.data == DISLIKE:
                # Removes the markup (buttons) after the user provides negative feedback.
                self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                self.bot.send_message(chat_id, self.assistant.negative_feedback(chat_id))
            """ The following block of code is commented out because it seems to deal with chat, email, or call responses
                which may not be currently implemented.
            elif call.data.startswith(CHAT_PREFIX):
                self.bot.send_message(chat_id, "chat")
            elif call.data.startswith(EMAIL_PREFIX):
                self.bot.send_message(chat_id, "email")
            elif call.data.startswith(CALL_PREFIX):
                self.bot.send_message(chat_id, "call") 
            """

    def process_request(self, chat_id: int, request: str):
        """
        Processes incoming text requests. Checks if the request results in a contact lookup and sends appropriate responses.

        :param chat_id: ID of the chat where the request came from.
        :param request: The user's message or recognized speech.
        """
        response = self.assistant.process_request(chat_id, request)  # Assistant processes the request.
        if self.is_contact_response(response):  # Checks if the response contains contact details.
            self.send_contacts(chat_id, response)  # Sends contact information if present.
            self.assistant.set_feedback(chat_id)  # Prepares for collecting feedback from the user.
            self.ask_for_feedback(chat_id)  # Ask the user for feedback (like/dislike).
        else:
            self.bot.send_message(chat_id, response)  # Sends a non-contact response message.

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
        return re.findall(fr"[\w._-]+@{self.domain}", text)  # Uses regular expressions to find emails matching the domain.

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
            contact = self.df[self.df["email"].str.contains(email, case=False, na=False)]  # Finds the contact info from the dataframe.
            
            def field(field_name: str) -> str:
                return contact[field_name].values[0]  # Helper function to fetch field values from the dataframe.

            markup = self.create_contact_markup(email)  # Creates contact action buttons (chat, email, call).
            # Sends the contact's name, position, and department in a markdown formatted message.
            self.bot.send_message(chat_id, f"*{field('name')}*\n{field('position')} @ {field('department')}", reply_markup=markup, parse_mode="markdown")

    def create_contact_markup(self, email: str) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with contact actions (chat, email, call).

        :param email: The email of the contact.
        :return: InlineKeyboardMarkup with buttons for chat, email, and call.
        """
        contact = self.df[self.df["email"].str.contains(email, case=False, na=False)]  # Finds the contact.
        phone_number = contact["phone"].values[0]  # Retrieves the phone number.

        # URLs for chat, email, and phone actions.
        telegram_url = f"https://t.me/AICentaurBot"  # Telegram deep link (placeholder).
        email_url = f"https://ai-hackathon-2024-redirect.j-konratt.workers.dev?email={email}"  # Email client link.
        tel_url = f"https://ai-hackathon-2024-redirect.j-konratt.workers.dev?tel={phone_number}"  # Phone call link.

        # Create the buttons for the chat, email, and call actions.
        markup = InlineKeyboardMarkup(row_width=3)  # Three buttons in a row.
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
        self.bot.infinity_polling()  # Starts the bot's polling mechanism for handling updates.