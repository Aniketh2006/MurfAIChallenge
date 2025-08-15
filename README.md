# 🎙️ 30 Days of MurfAI - Complete AI Voice Assistant

> **A production-ready AI conversational assistant that combines three powerful AI services to create natural voice-to-voice conversations with memory and context awareness.**

## 🌟 What Makes This Special?

This isn't just another chatbot - it's a **complete AI ecosystem** that demonstrates:

- 🧠 **Multi-AI Integration**: Seamlessly combines Murf AI, AssemblyAI, and Google Gemini
- 🗣️ **Natural Conversations**: Voice-to-voice interaction with context memory
- 🎭 **Multiple Personalities**: 6+ professional voices with different speaking styles
- 💾 **Session Memory**: Remembers your conversation across multiple interactions
- 🛡️ **Bulletproof Design**: Comprehensive error handling with graceful fallbacks
- 📱 **Universal Access**: Works on desktop, tablet, and mobile devices

## 📋 Table of Contents
- [🚀 Quick Start Guide](#-quick-start-guide)
- [🔑 Getting API Keys](#-getting-api-keys)
- [⚙️ Installation & Setup](#️-installation--setup)
- [📖 Complete User Guide](#-complete-user-guide)
- [🎯 Features Overview](#-features-overview)
- [🔧 API Reference](#-api-reference)
- [🛠️ Technical Details](#️-technical-details)
- [❓ Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start Guide

### ⏱️ 5-Minute Setup
1. **Install Python 3.8+** and ensure it's in your PATH
2. **Get API Keys** (see detailed section below)
3. **Run these commands:**
   ```bash
   # Clone or download the project
   cd "30 Days of MurfAI"
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate it (Windows)
   .\.venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file with your API keys
   # (See API Keys section below)
   
   # Start the server
   uvicorn main:app --reload
   ```
4. **Open** http://127.0.0.1:8000 in your browser
5. **Click the microphone** and start talking!

---

## 🔑 Getting API Keys

You need **three free API keys**. Here's exactly how to get each one:

### 1. 🎤 Murf AI API Key
1. Go to [murf.ai](https://murf.ai) and create a free account
2. Navigate to **API** section in your dashboard
3. Generate a new API key
4. Copy the key (starts with `ap2_...`)

### 2. 🎯 AssemblyAI API Key  
1. Visit [assemblyai.com](https://www.assemblyai.com/dashboard/signup)
2. Sign up for a free account
3. Go to your **Dashboard**
4. Copy your API key from the main dashboard

### 3. 🤖 Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key (starts with `AIzaSy...`)

### 📝 Create Your .env File
Create a file named `.env` in the project folder with this content:
```env
# Murf AI API key for text-to-speech
MURF_API_KEY=your_murf_api_key_here

# AssemblyAI API key for audio transcription
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Google Gemini API key for LLM functionality
GEMINI_API_KEY=your_gemini_api_key_here
```

⚠️ **Important**: Replace `your_*_api_key_here` with your actual API keys!

## ✨ Key Features

### 🤖 Conversational AI with Memory
- **Session-based Chat**: Maintains conversation history across multiple interactions
- **Google Gemini Integration**: Advanced LLM responses with context awareness
- **Voice-to-Voice Conversation**: Record audio questions, get spoken AI responses
- **Chat History Management**: View, clear, and manage conversation sessions

### 🎯 Text-to-Speech (Murf AI)
- **Professional Voice Generation**: High-quality TTS using Murf AI SDK
- **Multiple Voice Options**: Ken, Marcus, Claire, Charlie, Sarah, Natalie
- **Voice Styles**: Neutral, Cheerful, Angry, Sad, Excited, Whispering
- **Smart Text Processing**: Automatic truncation for TTS limits with intelligent sentence boundaries
- **Audio URL Generation**: Direct audio file URLs for immediate playback

### 🎙️ Audio Transcription (AssemblyAI)
- **High-Accuracy Transcription**: Convert voice recordings to text
- **Real-time Processing**: Fast transcription for conversational flow
- **Multiple Audio Format Support**: WAV, MP3, and other common formats
- **Confidence Scoring**: Quality metrics for transcription accuracy

### 🔄 Echo Bot & Voice Recording
- **Browser-based Recording**: MediaRecorder API integration
- **Echo Functionality**: Record voice, transcribe, and generate TTS response
- **Voice Recording Controls**: Start, stop, reset, and replay functionality
- **Audio Upload Support**: Upload pre-recorded audio files

### 🎨 Modern Web Interface
- **Multiple UI Templates**: Chat interface, LLM query page, and basic TTS generator
- **Dark Theme Design**: Professional appearance with responsive layout
- **Real-time Status Updates**: Loading indicators, progress tracking, error handling
- **Session Management**: Visual session IDs, message counters, and history controls

---

## ⚙️ Installation & Setup

### 📋 Prerequisites
- **Python 3.8 or higher** ([Download here](https://python.org/downloads/))
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Microphone access** for voice features
- **Internet connection** for AI services

### 🖥️ Windows Setup
```powershell
# Open PowerShell in the project directory
# If you get execution policy errors, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Start the application
uvicorn main:app --reload
```

### 🍎 macOS/Linux Setup
```bash
# Navigate to project directory
cd "30 Days of MurfAI"

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn main:app --reload
```

### ✅ Verify Installation
1. Open http://127.0.0.1:8000
2. You should see the AI Voice Assistant interface
3. Check http://127.0.0.1:8000/health for system status
4. All three services should show as "configured" and "initialized"

---

## 📖 Complete User Guide

### 🎯 Main Chat Interface (Default)
**URL**: http://127.0.0.1:8000

This is your primary interface for voice conversations with memory.

#### 🎤 How to Have a Voice Conversation:
1. **Start Recording**: Click the large microphone button (or press Spacebar)
2. **Speak Clearly**: Talk normally into your microphone
3. **Stop Recording**: Click the button again (or press Spacebar)
4. **Wait for Response**: The AI will:
   - Transcribe your speech (AssemblyAI)
   - Generate a response (Google Gemini)
   - Convert to speech (Murf AI)
   - Play the audio automatically

#### 💬 Session Features:
- **Session ID**: Automatically generated, shown in the top-right
- **Message History**: Scrollable conversation history
- **New Chat**: Click "New Chat" to start fresh
- **Memory**: Remembers up to 20 previous messages per session

#### ⌨️ Keyboard Shortcuts:
- **Spacebar**: Start/stop recording
- **Escape**: Cancel current recording
- **Ctrl+A**: Toggle auto-record mode

### 🎨 TTS Generator Interface
**URL**: Add `/templates/index.html` to any browser

Perfect for testing text-to-speech without conversation.

#### 📝 How to Generate Speech:
1. **Enter Text**: Type or paste text (up to 5000 characters)
2. **Choose Voice**: Select from Ken, Sarah, Marcus, or Claire
3. **Pick Style**: Choose Neutral, Cheerful, Excited, or Calm
4. **Generate**: Click "Generate Audio"
5. **Listen**: Use the custom audio player with volume/progress controls

#### 🎙️ Echo Bot Feature:
1. **Start Recording**: Click "Start Recording"
2. **Speak**: Talk into your microphone
3. **Stop Recording**: Click "Stop Recording"
4. **Listen**: Your voice will be transcribed and played back in a different voice

### 🤖 LLM Query Interface
**URL**: Add `/templates/index_llm.html` to any browser

For advanced text-based AI queries with optional voice input.

#### 💭 How to Query the AI:
1. **Text Input**: Type your question directly
2. **Voice Input**: Upload an audio file instead
3. **Submit**: Click "Send to AI"
4. **Response**: Get both text and audio responses

## 🏗️ Project Structure
```
30 Days of MurfAI/
├── main.py                 # FastAPI server (1,130 lines)
├── templates/
│   ├── chat.html          # Main chat interface
│   ├── index.html         # TTS generator + Echo bot
│   └── index_llm.html     # LLM query interface
├── static/
│   ├── script.js          # Frontend JavaScript
│   └── favicon.ico        # Website icon
├── .env                   # API keys (create this)
├── .venv/                 # Virtual environment (auto-created)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- API keys for:
  - Murf AI (text-to-speech): [Murf.ai](https://murf.ai)
  - AssemblyAI (transcription): [AssemblyAI](https://www.assemblyai.com)
  - Google Gemini (LLM): [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/30-days-of-murfai.git

# Navigate to project directory
cd "30-days-of-murfai"

# Create and activate virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:
```env
# Murf AI API key for text-to-speech
MURF_API_KEY=your_murf_api_key_here

# AssemblyAI API key for audio transcription
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Google Gemini API key for LLM functionality
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload
```

### 5. Access the Application
- **Main Chat Interface**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 🛠️ Technical Stack
- **Backend**: FastAPI with Python
- **AI Services**:
  - Murf AI SDK for text-to-speech
  - AssemblyAI for audio transcription
  - Google Gemini for LLM conversation
- **Frontend**: HTML5, CSS3, JavaScript
- **Browser APIs**: MediaRecorder for voice recording
- **Storage**: In-memory chat sessions (can be extended to persistent storage)

## 📱 How to Use

### Conversational Chat with Memory
1. The app automatically creates a new session or uses your existing one
2. Click the microphone button to start recording your question
3. Speak clearly into your microphone
4. The assistant transcribes your speech, processes with Gemini, and responds with Murf voice
5. Continue the conversation naturally - the assistant remembers previous messages

### TTS Generator
1. Enter text in the text area
2. Select a voice and speaking style
3. Click "Generate Audio" to create TTS audio
4. Use the audio player to listen to the generated speech

### Echo Bot
1. Start recording your voice
2. Speak into your microphone
3. Stop the recording when finished
4. The system will transcribe and echo back your message with a different voice

## 🔧 API Endpoints

### Chat Endpoints
- **POST** `/agent/chat/{session_id}`: Chat with voice input and TTS response
- **GET** `/agent/history/{session_id}`: Get chat history for a session
- **DELETE** `/agent/history/{session_id}`: Clear chat history
- **GET** `/agent/sessions`: List all active chat sessions

### Speech Endpoints
- **POST** `/tts/generate`: Generate TTS audio from text
- **POST** `/tts/echo`: Echo user's speech with Murf voice
- **GET** `/tts/voices`: List available voices and styles

### Audio Processing
- **POST** `/audio/upload`: Upload audio file
- **POST** `/transcribe/file`: Transcribe audio file
- **POST** `/llm/query`: Send text or audio to LLM and get TTS response

### System
- **GET** `/health`: System health check and feature list

## 🎯 Features Implemented
- ✅ **FastAPI Backend**: CORS-enabled API server with comprehensive documentation
- ✅ **Multi-AI Integration**: Murf AI, AssemblyAI, and Google Gemini services
- ✅ **Conversational Memory**: Session-based chat history management
- ✅ **Voice-to-Voice Chat**: Complete audio input to audio output pipeline
- ✅ **Professional TTS**: High-quality text-to-speech with multiple voices
- ✅ **Audio Transcription**: Real-time speech-to-text conversion
- ✅ **Echo Bot**: Voice recording with intelligent playback
- ✅ **Multiple UI Templates**: Chat, LLM, and TTS generator interfaces
- ✅ **Smart Text Processing**: Intelligent truncation and formatting
- ✅ **Session Management**: Create, track, and clear conversation sessions
- ✅ **Error Handling**: Graceful handling of API failures and edge cases
- ✅ **Modern UI**: Dark theme with responsive design

## 🧪 Testing
The application has been thoroughly tested with:
- ✅ Conversational AI with memory retention
- ✅ Voice-to-voice interactions
- ✅ Multiple TTS voices and styles
- ✅ Audio transcription accuracy
- ✅ Session management and history
- ✅ Error scenarios and edge cases
- ✅ Mobile and desktop responsiveness

## 🚧 Known Issues
- Requires active internet connection for all AI services
- Voice quality depends on user's microphone and browser support
- Some Murf voice IDs may not be available depending on your subscription plan
- Chat history is stored in memory (will be lost on server restart)
- Browser compatibility required for MediaRecorder API

## 🔮 Future Enhancements
- Persistent storage for chat history (database integration)
- Authentication and user accounts
- Fine-tuning of LLM responses
- Additional voice customization options
- Mobile app integration

## 📌 What Makes This Special

This isn't just another voice assistant - it's a **complete AI ecosystem** that demonstrates:

- **Multi-AI Integration**: Three different AI services working seamlessly together
- **Conversational Memory**: True back-and-forth dialogue with context retention
- **Voice-First Design**: Natural voice interactions from input to output
- **Professional Implementation**: Production-ready code with proper error handling
- **Extensible Architecture**: Easy to add new features and AI services

---

## 🎯 Features Overview

### 🗣️ Voice Features
| Feature | Description | Technology |
|---------|-------------|------------|
| **Voice Recording** | Browser-based audio capture | MediaRecorder API |
| **Speech Recognition** | Convert speech to text | AssemblyAI |
| **Text-to-Speech** | Convert text to natural speech | Murf AI |
| **Voice Selection** | 6+ professional voices | Murf AI Voices |
| **Style Control** | Multiple speaking styles | Murf AI Styles |

### 🧠 AI Features
| Feature | Description | Technology |
|---------|-------------|------------|
| **Conversational AI** | Context-aware responses | Google Gemini |
| **Memory System** | Remembers conversation history | Session-based storage |
| **Multi-turn Dialog** | Natural back-and-forth chat | Custom implementation |
| **Context Retention** | Maintains conversation context | LLM prompt engineering |

### 🎨 Interface Features
| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Dark Theme** | Professional appearance | CSS3 with animations |
| **Responsive Design** | Works on all screen sizes | Mobile-first CSS |
| **Real-time Status** | Live feedback on processing | JavaScript UI updates |
| **Session Management** | Multiple conversation tracking | Frontend + backend |
| **Audio Controls** | Custom audio player | HTML5 Audio API |

---

## 🔧 API Reference

### 🎤 Chat Endpoints

#### POST /agent/chat/{session_id}
**Purpose**: Main conversational endpoint with voice input
**Input**: Audio file (multipart/form-data)
**Output**: JSON with transcript, AI response, and audio URL

**Example Usage**:
```javascript
const formData = new FormData();
formData.append('audio_file', audioBlob, 'recording.webm');
const response = await fetch('/agent/chat/session_123', {
    method: 'POST',
    body: formData
});
```

#### GET /agent/history/{session_id}
**Purpose**: Retrieve conversation history
**Output**: List of messages with timestamps

#### DELETE /agent/history/{session_id}
**Purpose**: Clear conversation history
**Output**: Confirmation message

### 🎯 TTS Endpoints

#### POST /tts/generate
**Purpose**: Generate speech from text
**Input**: JSON with text, voice_id, and style
**Output**: Audio URL and metadata

**Example**:
```json
{
  "text": "Hello, this is a test",
  "voice_id": "en-US-ken",
  "style": "Cheerful"
}
```

#### POST /tts/echo
**Purpose**: Echo user's voice with different AI voice
**Input**: Audio file
**Output**: Transcription and new audio URL

### 🎙️ Audio Processing Endpoints

#### POST /transcribe/file
**Purpose**: Convert audio to text
**Input**: Audio file
**Output**: Transcript with confidence score

#### POST /llm/query
**Purpose**: Send text or audio to AI
**Input**: Text or audio file
**Output**: AI response with optional TTS audio

### 📄 System Endpoints

#### GET /health
**Purpose**: Check system status
**Output**: Service status and configuration info

#### GET /tts/voices
**Purpose**: List available voices and styles
**Output**: Voice options with metadata

---

## 🛠️ Technical Details

### 🏗️ Architecture Overview
```
Frontend (Browser)
    ↓ (Audio/Text)
FastAPI Server (main.py)
    ↓ (API Calls)
AI Services:
- AssemblyAI (Speech → Text)
- Google Gemini (Text → Response)
- Murf AI (Text → Speech)
```

### 🔧 Core Technologies
- **Backend**: FastAPI (Python web framework)
- **Frontend**: Vanilla JavaScript + HTML5 + CSS3
- **AI Services**: REST APIs
- **Audio**: MediaRecorder API, HTML5 Audio
- **Storage**: In-memory (easily upgradeable to database)

### 📄 Performance Characteristics
- **Startup Time**: ~3-5 seconds
- **Voice Processing**: ~2-5 seconds per request
- **Memory Usage**: ~50-100MB base + session data
- **Concurrent Users**: Limited by AI service quotas

---

## ❓ Troubleshooting

### 🚨 Common Issues & Solutions

#### "MURF_API_KEY not found"
- ✅ Check your `.env` file exists in the project root
- ✅ Verify API key is correct (starts with `ap2_`)
- ✅ No spaces or quotes around the key
- ✅ Restart the server after adding keys

#### "Microphone access denied"
- ✅ Allow microphone permission in browser
- ✅ Try HTTPS instead of HTTP (some browsers require it)
- ✅ Check if another app is using the microphone
- ✅ Test in an incognito window

#### "No speech detected in audio"
- ✅ Speak louder and more clearly
- ✅ Check microphone is working in other apps
- ✅ Try recording for at least 2-3 seconds
- ✅ Reduce background noise

#### Server won't start
- ✅ Check Python version: `python --version` (need 3.8+)
- ✅ Activate virtual environment first
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check port 8000 is available

#### Audio won't play
- ✅ Check browser audio settings
- ✅ Try a different browser
- ✅ Check internet connection
- ✅ Look for console errors (F12 → Console)

### 🔍 Debugging Steps

#### Check Service Status
1. Visit http://127.0.0.1:8000/health
2. All services should show "configured: true" and "initialized: true"
3. If not, check your API keys

#### Check Browser Console
1. Press F12 to open developer tools
2. Go to Console tab
3. Look for error messages in red
4. Common issues will be logged here

#### Verify API Keys
```bash
# In your project directory
cat .env
# Should show your three API keys
```

#### Test Individual Services
- **TTS Only**: Try the TTS generator page
- **Transcription Only**: Try the echo bot
- **LLM Only**: Try text input on LLM page

### 📞 Getting Help

#### Error Logs Location
- Browser: F12 → Console tab
- Server: Terminal where you ran `uvicorn main:app --reload`

#### What to Include When Asking for Help
1. Your operating system and Python version
2. Error messages (exact text)
3. Steps that led to the error
4. Browser console logs (if web-related)

---

## 🎉 You're All Set!

### 🚀 Quick Test Checklist
- [ ] Server starts without errors
- [ ] Health check shows all services configured
- [ ] Can record and hear your voice
- [ ] AI responds to your questions
- [ ] Can switch between different interfaces

### 🎯 What to Try First
1. **Simple greeting**: "Hello, how are you today?"
2. **Follow-up question**: "What's the weather like?"
3. **Test memory**: "What did I just ask you?"
4. **Try different voices**: Switch voices in TTS generator

### 🌟 Advanced Features to Explore
- Auto-record mode (Ctrl+A)
- Session history management
- Different speaking styles
- Multiple conversation sessions
- Echo bot with voice transformation

---

## 📅 Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs (when server is running)
- **Murf AI Docs**: [murf.ai/api](https://murf.ai/api)
- **AssemblyAI Docs**: [assemblyai.com/docs](https://www.assemblyai.com/docs)
- **Google Gemini Docs**: [ai.google.dev](https://ai.google.dev)

---

## 📱 Contact & Support

For questions, suggestions, or collaboration:
- Open an issue for bugs or feature requests
- Fork the repository to contribute improvements
- Share your voice assistant experiences!

## 📄 License

This project is part of the **30 Days of MurfAI** challenge - a journey to explore and implement cutting-edge voice AI technologies.

**Congratulations! You now have a fully functional AI voice assistant!** 🎆🤖✨

Start by saying "Hello" and watch the magic happen! 🎙️✨
