from dotenv import load_dotenv
from src.bot import Bot

load_dotenv()

Bot("rossmann-beispiel.de").start()
