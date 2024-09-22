
# AICentaurBot: Telegram Chat Bot for Finding the Right Contact Person within Rossmann

AICentaurBot is a Telegram bot designed to provide voice recognition and assistance based on user requests. The bot can handle text, voice commands, and retrieve relevant contact information from a dataset. The bot leverages the OpenAI API to process user input and respond intelligently based on user queries.

## Features

- **Text and Voice Command Processing**: The bot processes both text and voice commands from users.
- **Google Speech Recognition**: Converts voice messages into text using Google’s speech-to-text API.
- **Contact Retrieval**: Retrieves relevant contact persons based on the user's input, including department, position, responsibility, and location filters.
- **Multilingual**: Automatically detects and responds in the user's language based on their Telegram settings.

## Getting Started

### Prerequisites

To run the AICentaurBot locally, you need the following:

- Python 3.8 or higher
- A Telegram account
- A bot token from [Telegram BotFather](https://core.telegram.org/bots#botfather)
- An OpenAI API key (for handling complex requests)

### Install FFmpeg

The bot uses **FFmpeg** to convert voice messages from Telegram's OGG format to WAV, which is required for speech recognition. Follow these steps to install FFmpeg:

**On macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**On Ubuntu:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On Windows:**

1. Download the [FFmpeg executable](https://ffmpeg.org/download.html) for Windows.
2. Add the `bin` folder (where the `ffmpeg.exe` is located) to your system’s PATH.

You can verify if FFmpeg is installed by running:
```bash
ffmpeg -version
```

### Installation

1. **Clone the repository**:
   \`\`\`bash
   git clone https://github.com/CodesDoWork/ross-bot
   \`\`\`

2. **Install dependencies**:
   Install the required libraries by running:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Create a `.env` file**:
   Create a `.env` file to store your bot token and OpenAI API key. The file should look like this:
   \`\`\`bash
   BOT_TOKEN=<your-telegram-bot-token>
   OPENAI_API_KEY=<your-openai-api-key>
   \`\`\`

4. **Run the bot**:
   Start the bot by running:
   \`\`\`bash
   python src/main.py
   \`\`\`

### Customization

#### 1. **Telegram Custom Color Scheme**:
You can customize your Telegram experience by applying a custom color scheme. Here’s how:

- Open Telegram on your phone or desktop.
- Navigate to **Settings** > **Chat Settings**.
- Scroll down to **Change Chat Background** and choose a custom color scheme or apply the one provided with this code.

#### 2. **Disable Telegram's In-App Browser**:
To ensure that links (e.g., email or phone actions) are properly opened by external apps (and not within Telegram's browser), follow these steps:

- Open **Telegram** > **Settings** > **Data and Storage**.
- Scroll down to **In-App Browser** and turn it **off**.
- This allows links to open in the appropriate external apps (e.g., email or phone apps).

### Finding and Using the Bot

To search for and add the bot to your Telegram account, follow these steps:

1. Open the link to your bot provided by BotFather.
2. Click **Start** to initiate a conversation with the bot.
3. You can send both text and voice messages to interact with the bot. The bot will process your input and provide the relevant information or assistance.

### Bot Usage

1. **Greeting**: Type or say "Hello" to get a greeting from the bot.
2. **Voice Recognition**: Send a voice message, and the bot will transcribe it and process your request.
3. **Contact Retrieval**: Ask the bot to provide contacts based on departments, responsibilities, or location (e.g., "Show me people in the IT department").

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
