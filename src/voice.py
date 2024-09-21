import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from telebot import TeleBot
from telebot.types import Voice


class VoiceRecognizer:
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.recognizer = sr.Recognizer()

    def recognize_speech(self, voice: Voice) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
            file_path = temp_voice_file.name
            wav_file_path = file_path.replace(".ogg", ".wav")
            self.download_voice_to_file(voice, file_path)

        audio_data = self.extract_audio_data(file_path, wav_file_path)

        try:
            return self.recognizer.recognize_google(audio_data, language="de-DE")
        except sr.UnknownValueError:
            return "Entschuldigung, ich kann dich nicht verstehen."
        except sr.RequestError as e:
            print(f"Fehler bei der Spracherkennung: {e}")
            return "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        finally:
            os.remove(file_path)
            os.remove(wav_file_path)

    def download_voice_to_file(self, voice: Voice, file_path: str):
        file_info = self.bot.get_file(voice.file_id)
        downloaded_file = self.bot.download_file(file_info.file_path)
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)

    def extract_audio_data(self, file_path: str, wav_file_path: str) -> sr.AudioData:
        ogg_audio = AudioSegment.from_ogg(file_path)
        ogg_audio.export(wav_file_path, format="wav")
        with sr.AudioFile(wav_file_path) as source:
            return self.recognizer.record(source)