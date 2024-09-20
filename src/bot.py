# Import necessary modules and libraries
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command to initiate interaction with the bot."""
    re_text = 'Schick mir einen Text oder eine Sprachnachricht.'
    if update.message:
        await update.message.reply_text(re_text)

# Handle voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes voice messages, transcribes them, and sends the transcription to the chat."""
    voice = update.message.voice
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_voice_file:
        file_path = temp_voice_file.name

    wav_file_path = file_path.replace(".ogg", ".wav")

    if voice:
        # Download the voice message file
        file = await context.bot.get_file(voice.file_id)
        await file.download_to_drive(file_path)

    # Convert .ogg to .wav using pydub
    ogg_audio = AudioSegment.from_ogg(file_path)
    ogg_audio.export(wav_file_path, format="wav")

    with sr.AudioFile(wav_file_path) as source:
        # Recognize speech from the audio file
        audio_data = recognizer.record(source)
        try:
            # Transcribe the audio to text using Google's web-based recognizer
            text = recognizer.recognize_google(audio_data, language='de-DE')
            # Send the transcribed text back to the chat
            await update.message.reply_text(f'Transkribierter Text: {text}')
        except sr.UnknownValueError:
            await update.message.reply_text("Entschuldigung, ich kann dich nicht verstehen.")
        except sr.RequestError as e:
            await update.message.reply_text(f"Fehler bei der Spracherkennung: {e}")

    # Clean up temporary files
    os.remove(file_path)
    os.remove(wav_file_path)

# Handle text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the received text message back to the chat."""
    text = update.message.text
    await update.message.reply_text(f'Du hast gesagt: {text}')

def main() -> None:
    """Main function to run the bot."""
    app = Application.builder().token(BOT_TOKEN).build()  # Initialize the Telegram bot with the token

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start polling for updates
    app.run_polling()

# Run the main function if this script is executed
if __name__ == '__main__':
    main()
