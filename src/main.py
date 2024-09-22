"""
This script initializes and starts a Telegram bot for interacting with users. 
The bot's functionality is defined in the `Bot` class from the `src.bot` module. 
The script also loads environment variables from a `.env` file using the `dotenv` library.
"""

# Importing the `load_dotenv` function from the `dotenv` package.
# This function loads environment variables from a `.env` file into the system's environment variables, making them accessible in the code.
from dotenv import load_dotenv

# Importing the `Bot` class from the `src.bot` module.
# The `Bot` class defines all the functionality for the Telegram bot, including handling commands and user interactions.
from src.bot import Bot

# Loading environment variables from the `.env` file into the environment.
# This step ensures that any required environment variables, such as the bot token, are available for use.
load_dotenv()

# Creating an instance of the `Bot` class, passing in the domain "rossmann-beispiel.de".
# The domain is likely used for filtering or matching specific data within the bot's contact handling logic.
# The `start()` method begins the bot's event loop, allowing it to listen for incoming messages and respond to users.
Bot("rossmann-beispiel.de").start()
