import os  # For file operations such as removing temporary files.
import tempfile  # For creating temporary files to store downloaded audio.
import speech_recognition as sr  # For converting speech to text using Google's speech recognition API.
from pydub import AudioSegment  # For handling audio file format conversion (from .ogg to .wav).
from telebot import TeleBot  # For interacting with the Telegram API.
from telebot.types import Voice, User  # For handling voice message and user data from Telegram.


class VoiceRecognizer:
    def __init__(self, bot: TeleBot):
        """
        Initializes the VoiceRecognizer with a reference to the Telegram bot and a speech recognizer.

        :param bot: The TeleBot instance used to interact with Telegram's API.
        """
        self.bot = bot
        self.recognizer = sr.Recognizer()

    def recognize_speech(self, voice: Voice, user: User) -> str:
        """
        Downloads, converts, and transcribes a voice message into text based on the user's language.

        :param voice: The Voice message object from Telegram.
        :param user: The User object from Telegram, which contains user-specific data like the language code.
        :return: The transcribed text of the voice message or an error message.
        """
        language_code = user.language_code
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
            file_path = temp_voice_file.name
            wav_file_path = file_path.replace(".ogg", ".wav")
            self.download_voice_to_file(voice, file_path)

        audio_data = self.extract_audio_data(file_path, wav_file_path)

        try:
            return self.recognizer.recognize_google(audio_data, language=language_code)
        except sr.UnknownValueError:
            return "Entschuldigung, ich kann dich nicht verstehen."
        except sr.RequestError as e:
            print(f"Fehler bei der Spracherkennung: {e}")
            return "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        finally:
            os.remove(file_path)
            os.remove(wav_file_path)

    def download_voice_to_file(self, voice: Voice, file_path: str):
        """
        Downloads the voice message from Telegram and writes it to a file.

        :param voice: The Voice message object containing the file_id to download.
        :param file_path: The path where the downloaded voice message will be saved.
        """
        file_info = self.bot.get_file(voice.file_id)
        downloaded_file = self.bot.download_file(file_info.file_path)
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)

    def extract_audio_data(self, file_path: str, wav_file_path: str) -> sr.AudioData:
        """
        Converts an .ogg file to .wav format and extracts the audio data for speech recognition.

        :param file_path: The path to the .ogg file.
        :param wav_file_path: The path where the converted .wav file will be saved.
        :return: Audio data that can be processed by the speech recognizer.
        """
        ogg_audio = AudioSegment.from_ogg(file_path)
        ogg_audio.export(wav_file_path, format="wav")
        with sr.AudioFile(wav_file_path) as source:
            return self.recognizer.record(source)
