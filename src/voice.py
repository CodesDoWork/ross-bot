"""
This script defines the `VoiceRecognizer` class, which integrates speech recognition capabilities into a Telegram bot. 
It handles the process of downloading voice messages from Telegram, converting them to a recognizable audio format, 
and using Google's speech recognition API to transcribe the voice message into text based on the user's language settings.
"""

# Import necessary libraries and modules.
import os  # For file operations such as removing temporary files.
import tempfile  # For creating temporary files to store downloaded audio.
import speech_recognition as sr  # For converting speech to text using Google's speech recognition API.
from pydub import AudioSegment  # For handling audio file format conversion (from .ogg to .wav).
from telebot import TeleBot  # For interacting with the Telegram API.
from telebot.types import Voice, User  # For handling voice message and user data from Telegram.

# Define the VoiceRecognizer class, which handles voice recognition for the Telegram bot.
class VoiceRecognizer:
    def __init__(self, bot: TeleBot):
        """
        Initializes the VoiceRecognizer with a reference to the Telegram bot and a speech recognizer.

        :param bot: The TeleBot instance used to interact with Telegram's API.
        """
        self.bot = bot
        # Initialize a speech recognizer from the speech_recognition library.
        self.recognizer = sr.Recognizer()

    # Recognizes and transcribes a user's speech from a voice message.
    def recognize_speech(self, voice: Voice, user: User) -> str:
        """
        Downloads, converts, and transcribes a voice message into text based on the user's language.

        :param voice: The Voice message object from Telegram.
        :param user: The User object from Telegram, which contains user-specific data like the language code.
        :return: The transcribed text of the voice message or an error message.
        """
        # Get the user's language code for use in the speech recognition process.
        language_code = user.language_code
        
        # Create a temporary file to store the downloaded voice message in .ogg format.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
            file_path = temp_voice_file.name  # Get the file path for the temporary .ogg file.
            wav_file_path = file_path.replace(".ogg", ".wav")  # Define the path for the converted .wav file.
            # Download the voice message and save it to the temporary .ogg file.
            self.download_voice_to_file(voice, file_path)

        # Extract the audio data by converting the .ogg file to .wav format.
        audio_data = self.extract_audio_data(file_path, wav_file_path)

        try:
            # Use Google's speech recognition service to transcribe the audio data into text.
            return self.recognizer.recognize_google(audio_data, language=language_code)
        except sr.UnknownValueError:
            # Handle the case where the speech could not be understood.
            return "Entschuldigung, ich kann dich nicht verstehen."
        except sr.RequestError as e:
            # Handle any errors that occur while communicating with the speech recognition service.
            print(f"Fehler bei der Spracherkennung: {e}")
            return "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        finally:
            # Clean up by removing the temporary .ogg and .wav files.
            os.remove(file_path)
            os.remove(wav_file_path)

    # Downloads the voice message from Telegram and saves it to a specified file path.
    def download_voice_to_file(self, voice: Voice, file_path: str):
        """
        Downloads the voice message from Telegram and writes it to a file.

        :param voice: The Voice message object containing the file_id to download.
        :param file_path: The path where the downloaded voice message will be saved.
        """
        # Get the file information (file path on Telegram's servers) using the file ID.
        file_info = self.bot.get_file(voice.file_id)
        # Download the file from Telegram's servers.
        downloaded_file = self.bot.download_file(file_info.file_path)
        # Write the downloaded data to the specified file path.
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)

    # Converts the downloaded .ogg file to .wav and extracts audio data for speech recognition.
    def extract_audio_data(self, file_path: str, wav_file_path: str) -> sr.AudioData:
        """
        Converts an .ogg file to .wav format and extracts the audio data for speech recognition.

        :param file_path: The path to the .ogg file.
        :param wav_file_path: The path where the converted .wav file will be saved.
        :return: Audio data that can be processed by the speech recognizer.
        """
        # Load the .ogg file using the pydub library.
        ogg_audio = AudioSegment.from_ogg(file_path)
        # Export the audio as a .wav file.
        ogg_audio.export(wav_file_path, format="wav")
        # Load the .wav file into the speech_recognition library.
        with sr.AudioFile(wav_file_path) as source:
            # Return the audio data extracted from the .wav file.
            return self.recognizer.record(source)
