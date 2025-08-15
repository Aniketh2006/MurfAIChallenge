# Import necessary libraries
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request, Path
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

# Import AI service libraries
from murf import Murf  # Text-to-Speech
import assemblyai as aai  # Speech-to-Text
import google.generativeai as genai  # Large Language Model

# Load environment variables
load_dotenv()

app = FastAPI(
    title="30 Days of MurfAI - Conversational AI Assistant",
    description="Complete voice assistant with chat history and memory using Murf AI, AssemblyAI, and Gemini",
    version="4.0.0"
)

# In-memory chat history storage (session_id -> list of messages)
# For production, consider using Redis, PostgreSQL, or other persistent storage
chat_sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)

# Maximum messages to keep in history (to prevent token limits)
MAX_HISTORY_MESSAGES = 20

# Error handling configuration
FALLBACK_MESSAGES = {
    "stt_error": "I'm having trouble hearing you right now. Please check your microphone and try again.",
    "llm_error": "I'm having trouble thinking right now. My AI brain needs a moment to reconnect.",
    "tts_error": "I'm having trouble speaking right now, but I can still understand you.",
    "connection_error": "I'm having trouble connecting to my services right now. Please try again in a moment.",
    "general_error": "Something went wrong on my end. Let me try to help you differently."
}

# Utility functions for error handling
def get_error_type(exception: Exception) -> str:
    """Determine the type of error based on the exception"""
    error_str = str(exception).lower()
    
    if "assemblyai" in error_str or "transcription" in error_str or "speech" in error_str:
        return "stt_error"
    elif "gemini" in error_str or "llm" in error_str or "generate_content" in error_str:
        return "llm_error"
    elif "murf" in error_str or "tts" in error_str or "text_to_speech" in error_str:
        return "tts_error"
    elif "connection" in error_str or "network" in error_str or "timeout" in error_str:
        return "connection_error"
    else:
        return "general_error"

def generate_fallback_tts(message: str, voice: str = "en-US-ken", style: str = "Neutral") -> Optional[str]:
    """Generate fallback TTS audio if Murf is available"""
    if not murf_client:
        return None
    
    try:
        response = murf_client.text_to_speech.generate(
            text=message,
            voice_id=voice,
            style=style
        )
        
        if hasattr(response, 'audio_url'):
            return response.audio_url
        elif hasattr(response, 'audio_file'):
            return str(response.audio_file)
        else:
            return str(response)
    except Exception as e:
        print(f"⚠️ Fallback TTS also failed: {str(e)}")
        return None

def safe_transcribe_audio(audio_data: bytes) -> tuple[Optional[str], Optional[str]]:
    """Safely transcribe audio with error handling. Returns (transcript, error_message)"""
    if not aai_transcriber:
        return None, "Speech-to-text service is not available"
    
    try:
        transcript = aai_transcriber.transcribe(audio_data)
        
        if transcript.status == aai.TranscriptStatus.error:
            return None, f"Transcription failed: {transcript.error}"
        
        text = transcript.text
        if not text or len(text.strip()) == 0:
            return None, "No speech detected in the audio"
        
        return text.strip(), None
    except Exception as e:
        error_msg = f"Transcription error: {str(e)}"
        print(f"❌ {error_msg}")
        return None, error_msg

def safe_generate_llm_response(prompt: str) -> tuple[Optional[str], Optional[str]]:
    """Safely generate LLM response. Returns (response, error_message)"""
    if not gemini_client:
        return None, "AI language model is not available"
    
    try:
        llm_response = gemini_client.generate_content(prompt)
        
        if not llm_response.text:
            return None, "AI did not generate a response"
        
        return llm_response.text.strip(), None
    except Exception as e:
        error_msg = f"AI response error: {str(e)}"
        print(f"❌ {error_msg}")
        return None, error_msg

def safe_generate_tts(text: str, voice: str = "en-US-claire", style: str = "Cheerful") -> tuple[Optional[str], Optional[str]]:
    """Safely generate TTS audio. Returns (audio_url, error_message)"""
    if not murf_client:
        return None, "Text-to-speech service is not available"
    
    try:
        response = murf_client.text_to_speech.generate(
            text=text,
            voice_id=voice,
            style=style
        )
        
        audio_url = None
        if hasattr(response, 'audio_url'):
            audio_url = response.audio_url
        elif hasattr(response, 'audio_file'):
            audio_url = str(response.audio_file)
        else:
            audio_url = str(response)
        
        return audio_url, None
    except Exception as e:
        error_msg = f"Text-to-speech error: {str(e)}"
        print(f"❌ {error_msg}")
        return None, error_msg

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Murf client
MURF_API_KEY = os.getenv("MURF_API_KEY")
if not MURF_API_KEY:
    print("⚠️ Warning: MURF_API_KEY not found in environment variables!")
    murf_client = None
else:
    murf_client = Murf(api_key=MURF_API_KEY)
    print("✅ Murf client initialized successfully!")

# Initialize AssemblyAI client
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    print("⚠️ Warning: ASSEMBLYAI_API_KEY not found in environment variables!")
    aai_transcriber = None
else:
    aai.settings.api_key = ASSEMBLYAI_API_KEY
    aai_transcriber = aai.Transcriber()
    print("✅ AssemblyAI client initialized successfully!")

# Initialize Google Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables!")
    gemini_client = None
else:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_client = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Google Gemini client initialized successfully!")

# Pydantic models for request/response
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-ken"  # Default voice
    style: str = "Neutral"  # Default style
    
class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_url: str = None
    audio_file: str = None
    word_count: int = None

class AudioUploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    content_type: str
    size: int

class TranscriptionResponse(BaseModel):
    success: bool
    message: str
    transcript: Optional[str] = None
    confidence: Optional[float] = None
    language_detected: Optional[str] = None

class LLMRequest(BaseModel):
    text: str

class LLMResponse(BaseModel):
    success: bool
    message: str
    response: Optional[str] = None
    model: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    llm_response: Optional[str] = None
    session_id: str
    message_count: int
    error_type: Optional[str] = None
    fallback_used: Optional[bool] = False

class ErrorResponse(BaseModel):
    success: bool = False
    error_type: str
    message: str
    fallback_message: Optional[str] = None
    audio_url: Optional[str] = None
    suggestions: Optional[List[str]] = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main AI Chat Assistant page with conversation memory"""
    try:
        # Try to load the new chat template first
        with open("templates/chat.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        try:
            # Try the LLM template as fallback
            with open("templates/index_llm.html", "r", encoding="utf-8") as file:
                html_content = file.read()
            return HTMLResponse(content=html_content, status_code=200)
        except FileNotFoundError:
            try:
                # Fallback to original template if others don't exist
                with open("templates/index.html", "r", encoding="utf-8") as file:
                    html_content = file.read()
                return HTMLResponse(content=html_content, status_code=200)
            except FileNotFoundError:
                return HTMLResponse(
                    content="<h1>AI Chat Assistant</h1><p>Template not found, but API is working at /docs</p>", 
                    status_code=200
                )

@app.post("/tts/generate", response_model=TTSResponse, summary="Generate TTS Audio", description="Convert text to speech using Murf Python SDK")
async def generate_tts(request: TTSRequest):
    """
    Generate text-to-speech audio using Murf's Python SDK
    
    - **text**: The text to convert to speech (required)
    - **voice_id**: The voice ID to use (default: en-US-ken)
    - **style**: The speaking style (default: Neutral)
    """
    
    # Check if API key is configured
    if not murf_client:
        raise HTTPException(
            status_code=500, 
            detail="MURF_API_KEY not found in environment variables. Please add it to your .env file."
        )
    
    # Validate text length
    if len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )
    
    if len(request.text) > 5000:  # Reasonable limit
        raise HTTPException(
            status_code=400,
            detail="Text is too long. Please limit to 5000 characters."
        )
    
    try:
        print(f"🎤 Generating TTS for: '{request.text[:50]}...'")
        print(f"🗣️ Voice: {request.voice_id}, Style: {request.style}")
        
        # Use Murf SDK to generate speech
        response = murf_client.text_to_speech.generate(
            text=request.text.strip(),
            voice_id=request.voice_id,
            style=request.style
        )
        
        # Extract audio URL from response
        audio_url = None
        if hasattr(response, 'audio_url'):
            audio_url = response.audio_url
        elif hasattr(response, 'audio_file'):
            audio_url = str(response.audio_file)
        else:
            # Try to get URL from response object
            audio_url = str(response)
        
        print(f"✅ TTS generated successfully! Audio URL: {audio_url}")
        
        # Return success response
        return TTSResponse(
            success=True,
            message="TTS generation successful!",
            audio_url=audio_url,
            audio_file=str(response.audio_file) if hasattr(response, 'audio_file') else audio_url,
            word_count=len(request.text.split())
        )
        
    except Exception as e:
        print(f"❌ Murf SDK error: {str(e)}")
        # Handle any errors from the Murf SDK
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )

@app.get("/tts/voices", summary="List Available Voices", description="Get list of available TTS voices")
async def list_voices():
    """
    Get list of popular TTS voices available in Murf
    """
    # Return some popular voice options
    return {
        "message": "Popular Murf voices",
        "voices": [
            {"id": "en-US-ken", "name": "Ken", "language": "English (US)", "gender": "male"},
            {"id": "en-US-sarah", "name": "Sarah", "language": "English (US)", "gender": "female"},
            {"id": "en-US-marcus", "name": "Marcus", "language": "English (US)", "gender": "male"},
            {"id": "en-UK-charlie", "name": "Charlie", "language": "English (UK)", "gender": "male"},
            {"id": "en-US-claire", "name": "Claire", "language": "English (US)", "gender": "female"}
        ],
        "styles": ["Neutral", "Cheerful", "Angry", "Sad", "Excited", "Whispering"]
    }

@app.post("/audio/upload", response_model=AudioUploadResponse, summary="Upload Audio File", description="Upload recorded audio file to server")
async def upload_audio(audio_file: UploadFile = File(...)):
    """
    Upload recorded audio file to the server
    
    - **audio_file**: The audio file to upload (required)
    """
    
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed."
            )
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'
        unique_filename = f"recording_{timestamp}.{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        print(f"🎵 Audio file uploaded successfully!")
        print(f"📁 Filename: {unique_filename}")
        print(f"📊 Size: {file_size} bytes")
        print(f"🎧 Content Type: {audio_file.content_type}")
        
        # Return success response
        return AudioUploadResponse(
            success=True,
            message="Audio file uploaded successfully!",
            filename=unique_filename,
            content_type=audio_file.content_type,
            size=file_size
        )
        
    except Exception as e:
        print(f"❌ Audio upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload audio file: {str(e)}"
        )

@app.post("/transcribe/file", response_model=TranscriptionResponse, summary="Transcribe Audio File", description="Transcribe audio file to text using AssemblyAI")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe audio file to text using AssemblyAI
    
    - **audio_file**: The audio file to transcribe (required)
    """
    
    try:
        # Check if AssemblyAI is configured
        if not aai_transcriber:
            raise HTTPException(
                status_code=500,
                detail="ASSEMBLYAI_API_KEY not found in environment variables. Please add it to your .env file."
            )
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed."
            )
        
        print(f"🎤 Starting transcription for: {audio_file.filename}")
        print(f"🎧 Content Type: {audio_file.content_type}")
        
        # Read audio file data
        audio_data = await audio_file.read()
        print(f"📊 Audio data size: {len(audio_data)} bytes")
        
        # Transcribe using AssemblyAI
        transcript = aai_transcriber.transcribe(audio_data)
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        print(f"✅ Transcription completed successfully!")
        print(f"📝 Transcript: {transcript.text[:100]}...")
        print(f"🎯 Confidence: {transcript.confidence}")
        
        # Return success response
        return TranscriptionResponse(
            success=True,
            message="Audio transcription completed successfully!",
            transcript=transcript.text,
            confidence=transcript.confidence,
            language_detected=transcript.language_code if hasattr(transcript, 'language_code') else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

@app.post("/tts/echo", response_model=TTSResponse, summary="Echo Bot with Murf Voice", description="Transcribe audio and echo back with Murf voice")
async def echo_with_murf(audio_file: UploadFile = File(...)):
    """
    Echo Bot endpoint that transcribes audio and regenerates it with Murf voice
    
    - **audio_file**: The audio file to transcribe and echo back (required)
    """
    
    try:
        # Check if both APIs are configured
        if not aai_transcriber:
            raise HTTPException(
                status_code=500,
                detail="ASSEMBLYAI_API_KEY not found in environment variables. Please add it to your .env file."
            )
        
        if not murf_client:
            raise HTTPException(
                status_code=500,
                detail="MURF_API_KEY not found in environment variables. Please add it to your .env file."
            )
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed."
            )
        
        print(f"🎤 Echo Bot: Processing {audio_file.filename}")
        print(f"🎧 Content Type: {audio_file.content_type}")
        
        # Step 1: Read and transcribe audio
        audio_data = await audio_file.read()
        print(f"📊 Audio data size: {len(audio_data)} bytes")
        
        print("📝 Transcribing audio with AssemblyAI...")
        transcript = aai_transcriber.transcribe(audio_data)
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        transcribed_text = transcript.text
        if not transcribed_text or len(transcribed_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="No speech detected in the audio. Please record clear audio with speech."
            )
        
        # Clean up the transcribed text
        transcribed_text = transcribed_text.strip()
        
        print(f"✅ Transcription successful: {transcribed_text[:100]}...")
        print(f"🎯 Confidence: {transcript.confidence}")
        
        # Step 2: Generate speech with Murf using the transcribed text
        # Using a different voice for variety - you can change this
        murf_voice = "en-US-natalie"  # Female voice for contrast
        murf_style = "Neutral"  # Using Neutral style as it's more reliable
        
        print(f"🎤 Generating speech with Murf voice: {murf_voice}")
        print(f"🗣️ Style: {murf_style}")
        
        response = murf_client.text_to_speech.generate(
            text=transcribed_text,
            voice_id=murf_voice,
            style=murf_style
        )
        
        # Extract audio URL from response
        audio_url = None
        if hasattr(response, 'audio_url'):
            audio_url = response.audio_url
        elif hasattr(response, 'audio_file'):
            audio_url = str(response.audio_file)
        else:
            audio_url = str(response)
        
        print(f"✅ Murf audio generated successfully! URL: {audio_url}")
        
        # Return success response with both transcript and audio URL
        return TTSResponse(
            success=True,
            message=f"Echo generated with Murf voice! Transcript: {transcribed_text}",
            audio_url=audio_url,
            audio_file=str(response.audio_file) if hasattr(response, 'audio_file') else audio_url,
            word_count=len(transcribed_text.split())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Echo Bot error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process echo: {str(e)}"
        )

@app.post("/llm/query", response_model=TTSResponse, summary="Query LLM with Audio/Text", description="Accept audio or text input, query Gemini LLM, and return Murf audio response")
async def query_llm(
    request: Request,
    text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None)
):
    """
    Accept audio or text input, send to Google Gemini LLM, and return Murf-generated audio response
    
    - **text**: Optional text query to send to the LLM
    - **audio_file**: Optional audio file to transcribe and send to the LLM
    """
    
    try:
        # Check if all required services are configured
        if not gemini_client:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not found in environment variables. Please add it to your .env file."
            )
        
        if not murf_client:
            raise HTTPException(
                status_code=500,
                detail="MURF_API_KEY not found in environment variables. Please add it to your .env file."
            )
        
        # Step 1: Get the query text (either from JSON body, form data, or transcribed audio)
        query_text = ""
        
        # Check if it's a JSON request
        content_type = request.headers.get("content-type", "")
        
        if audio_file:
            # Handle audio file upload
            # Check if AssemblyAI is configured for transcription
            if not aai_transcriber:
                raise HTTPException(
                    status_code=500,
                    detail="ASSEMBLYAI_API_KEY not found in environment variables. Please add it to your .env file."
                )
            
            # Validate audio file type
            if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only audio files are allowed."
                )
            
            print(f"🎤 Transcribing audio for LLM query: {audio_file.filename}")
            
            # Transcribe the audio
            audio_data = await audio_file.read()
            transcript = aai_transcriber.transcribe(audio_data)
            
            # Check if transcription was successful
            if transcript.status == aai.TranscriptStatus.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription failed: {transcript.error}"
                )
            
            query_text = transcript.text
            if not query_text or len(query_text.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No speech detected in the audio. Please record clear audio with speech."
                )
            
            print(f"✅ Transcription successful: {query_text[:100]}...")
            
        elif "application/json" in content_type:
            # Handle JSON request
            try:
                body = await request.json()
                query_text = body.get("text", "").strip()
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON in request body"
                )
        elif text:
            # Handle form data text
            query_text = text.strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="Either text or audio_file must be provided."
            )
        
        # Validate query text length
        if len(query_text) == 0:
            raise HTTPException(
                status_code=400,
                detail="Query text cannot be empty."
            )
        
        if len(query_text) > 8000:  # Reasonable limit for Gemini
            raise HTTPException(
                status_code=400,
                detail="Query text is too long. Please limit to 8000 characters."
            )
        
        # Step 2: Send query to Gemini LLM
        print(f"🤖 Sending query to Gemini: '{query_text[:50]}...'")
        
        llm_response = gemini_client.generate_content(query_text)
        
        # Check if response was generated successfully
        if not llm_response.text:
            raise HTTPException(
                status_code=500,
                detail="LLM did not generate a response. Please try again with different text."
            )
        
        llm_text = llm_response.text.strip()
        print(f"✅ Gemini response generated: {llm_text[:100]}...")
        print(f"📏 Original response length: {len(llm_text)} characters")
        
        # Truncate text if it exceeds Murf's limit (3000 characters)
        MAX_MURF_CHARS = 3000
        full_response = llm_text  # Keep the full response for the message
        
        if len(llm_text) > MAX_MURF_CHARS:
            # Truncate intelligently at a sentence boundary if possible
            truncated_text = llm_text[:MAX_MURF_CHARS]
            
            # Try to find the last complete sentence
            last_period = truncated_text.rfind('.')
            last_exclamation = truncated_text.rfind('!')
            last_question = truncated_text.rfind('?')
            
            # Find the last sentence ending
            last_sentence_end = max(last_period, last_exclamation, last_question)
            
            if last_sentence_end > MAX_MURF_CHARS * 0.8:  # If we have at least 80% of the text with a complete sentence
                llm_text = truncated_text[:last_sentence_end + 1]
            else:
                # Otherwise, truncate at word boundary
                last_space = truncated_text.rfind(' ')
                if last_space > MAX_MURF_CHARS * 0.9:
                    llm_text = truncated_text[:last_space] + "..."
                else:
                    llm_text = truncated_text + "..."
            
            print(f"⚠️ Response truncated from {len(full_response)} to {len(llm_text)} characters for Murf TTS")
            print(f"📝 Truncated at: ...{llm_text[-50:]}")
        
        # Step 3: Generate Murf audio from LLM response
        print(f"🎤 Generating Murf audio for LLM response...")
        
        # Use a professional voice for LLM responses
        murf_voice = "en-US-marcus"  # Professional male voice
        murf_style = "Neutral"
        
        murf_response = murf_client.text_to_speech.generate(
            text=llm_text,
            voice_id=murf_voice,
            style=murf_style
        )
        
        # Extract audio URL from response
        audio_url = None
        if hasattr(murf_response, 'audio_url'):
            audio_url = murf_response.audio_url
        elif hasattr(murf_response, 'audio_file'):
            audio_url = str(murf_response.audio_file)
        else:
            audio_url = str(murf_response)
        
        print(f"✅ Murf audio generated successfully! URL: {audio_url}")
        
        # Step 4: Return the audio response with metadata
        # Use the full response for the message display but the truncated version was used for audio
        display_message = full_response if 'full_response' in locals() else llm_text
        was_truncated = len(full_response) > MAX_MURF_CHARS if 'full_response' in locals() else False
        
        response_message = f"LLM responded: {display_message[:500]}{'...' if len(display_message) > 500 else ''}"
        if was_truncated:
            response_message += f" (Note: Audio response was truncated to {MAX_MURF_CHARS} characters due to TTS limits)"
        
        return TTSResponse(
            success=True,
            message=response_message,
            audio_url=audio_url,
            audio_file=str(murf_response.audio_file) if hasattr(murf_response, 'audio_file') else audio_url,
            word_count=len(llm_text.split())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ LLM Query error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process LLM query: {str(e)}"
        )

@app.post("/agent/chat/{session_id}", response_model=ChatResponse, summary="Robust Conversational Chat with Memory", description="Chat endpoint with comprehensive error handling and fallback mechanisms")
async def chat_with_history(
    session_id: str = Path(..., description="Unique session identifier for conversation history"),
    audio_file: UploadFile = File(..., description="Audio file containing user's message")
):
    """
    🛡️ ROBUST Chat endpoint with conversation history and comprehensive error handling.
    Maintains conversation context across multiple messages with fallback mechanisms.
    
    Features:
    - Graceful degradation when services fail
    - Fallback audio responses
    - Detailed error reporting
    - Service health monitoring
    
    - **session_id**: Unique identifier for the conversation session
    - **audio_file**: Audio file containing the user's message
    """
    
    # Initialize variables for tracking errors
    transcript_error = None
    llm_error = None
    tts_error = None
    fallback_used = False
    error_type = None
    user_message = None
    assistant_message = None
    audio_url = None
    
    try:
        print(f"\n{'='*60}")
        print(f"🛡️ ROBUST CHAT SESSION STARTED")
        print(f"🎭 Session ID: {session_id}")
        print(f"📝 Current message count in session: {len(chat_sessions[session_id])}")
        print(f"🎤 Processing audio: {audio_file.filename}")
        
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are allowed."
            )
        
        # STEP 1: TRANSCRIBE AUDIO WITH ERROR HANDLING
        print("\n🎯 1️⃣ TRANSCRIBING AUDIO (with fallback)...")
        audio_data = await audio_file.read()
        print(f"📊 Audio data size: {len(audio_data)} bytes")
        
        user_message, transcript_error = safe_transcribe_audio(audio_data)
        
        if transcript_error:
            print(f"🔴 STT Error: {transcript_error}")
            error_type = "stt_error"
            fallback_message = FALLBACK_MESSAGES[error_type]
            
            # Try to generate fallback audio
            fallback_audio = generate_fallback_tts(fallback_message)
            
            return ChatResponse(
                success=False,
                message=fallback_message,
                audio_url=fallback_audio,
                transcript=None,
                llm_response=fallback_message,
                session_id=session_id,
                message_count=len(chat_sessions[session_id]),
                error_type=error_type,
                fallback_used=True
            )
        
        print(f"✅ STT Success: '{user_message[:100]}...'")
        
        # Add user message to chat history
        chat_sessions[session_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # STEP 2: PREPARE CONVERSATION CONTEXT
        print(f"\n🎯 2️⃣ PREPARING CONVERSATION CONTEXT...")
        
        # Get recent messages from history (limit to prevent token overflow)
        recent_messages = chat_sessions[session_id][-MAX_HISTORY_MESSAGES:]
        
        # Build conversation prompt
        conversation_prompt = "You are a helpful AI assistant. Here is our conversation so far:\n\n"
        
        for msg in recent_messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            conversation_prompt += f"{role_label}: {msg['content']}\n\n"
        
        # If this is continuing a conversation, add context
        if len(recent_messages) > 1:
            conversation_prompt += "Please continue our conversation naturally, remembering what we discussed earlier.\n"
        
        print(f"📜 Context includes {len(recent_messages)} messages")
        print(f"📏 Total prompt length: {len(conversation_prompt)} characters")
        
        # STEP 3: GENERATE LLM RESPONSE WITH ERROR HANDLING
        print(f"\n🎯 3️⃣ GENERATING LLM RESPONSE (with fallback)...")
        
        assistant_message, llm_error = safe_generate_llm_response(conversation_prompt)
        
        if llm_error:
            print(f"🔴 LLM Error: {llm_error}")
            error_type = "llm_error"
            assistant_message = FALLBACK_MESSAGES[error_type]
            fallback_used = True
            print(f"🔄 Using fallback response: '{assistant_message}'")
        else:
            print(f"✅ LLM Success: '{assistant_message[:100]}...'")
        
        # Add assistant response to chat history
        chat_sessions[session_id].append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # STEP 4: PREPARE TEXT FOR TTS (with intelligent truncation)
        print(f"\n🎯 4️⃣ PREPARING TEXT FOR TTS...")
        MAX_MURF_CHARS = 3000
        tts_text = assistant_message
        
        if len(tts_text) > MAX_MURF_CHARS:
            # Intelligent truncation
            truncated = tts_text[:MAX_MURF_CHARS]
            last_sentence = max(
                truncated.rfind('.'),
                truncated.rfind('!'),
                truncated.rfind('?')
            )
            
            if last_sentence > MAX_MURF_CHARS * 0.8:
                tts_text = truncated[:last_sentence + 1]
            else:
                last_space = truncated.rfind(' ')
                tts_text = truncated[:last_space] if last_space > 0 else truncated
                tts_text += "..."
            
            print(f"⚠️ Response truncated for TTS: {len(assistant_message)} → {len(tts_text)} chars")
        
        # STEP 5: GENERATE TTS AUDIO WITH ERROR HANDLING
        print(f"\n🎯 5️⃣ GENERATING TTS AUDIO (with fallback)...")
        
        # Choose voice based on whether we're using fallback or not
        voice = "en-US-ken" if fallback_used else "en-US-claire"
        style = "Neutral" if fallback_used else "Cheerful"
        
        print(f"🎤 Voice: {voice}, Style: {style}")
        
        audio_url, tts_error = safe_generate_tts(tts_text, voice, style)
        
        if tts_error:
            print(f"🔴 TTS Error: {tts_error}")
            if not error_type:  # Only set error type if not already set
                error_type = "tts_error"
            # TTS failed, but we still have the text response
            print(f"⚠️ Audio unavailable, but text response available")
        else:
            print(f"✅ TTS Success: {audio_url}")
        
        # STEP 6: CLEANUP AND FINALIZATION
        print(f"\n🎯 6️⃣ FINALIZING RESPONSE...")
        
        # Clean up old messages if history is too long
        if len(chat_sessions[session_id]) > MAX_HISTORY_MESSAGES * 2:
            chat_sessions[session_id] = chat_sessions[session_id][-MAX_HISTORY_MESSAGES:]
            print(f"🧹 Cleaned up old messages, kept last {MAX_HISTORY_MESSAGES}")
        
        # Determine success status
        overall_success = not (transcript_error or (llm_error and not fallback_used))
        
        # Create status message
        status_parts = []
        if transcript_error:
            status_parts.append("❌ Speech recognition failed")
        else:
            status_parts.append("✅ Speech recognized")
            
        if llm_error:
            status_parts.append("🔄 Using fallback response")
        else:
            status_parts.append("✅ AI response generated")
            
        if tts_error:
            status_parts.append("⚠️ Audio generation failed")
        else:
            status_parts.append("✅ Audio generated")
        
        status_message = " | ".join(status_parts)
        
        print(f"\n{'='*60}")
        print(f"📊 FINAL STATUS: {status_message}")
        print(f"🎭 Session Messages: {len(chat_sessions[session_id])}")
        print(f"🔄 Fallback Used: {fallback_used}")
        print(f"🎵 Audio Available: {bool(audio_url)}")
        print(f"{'='*60}\n")
        
        # Return comprehensive response
        return ChatResponse(
            success=overall_success,
            message=status_message,
            audio_url=audio_url,
            transcript=user_message,
            llm_response=assistant_message,
            session_id=session_id,
            message_count=len(chat_sessions[session_id]),
            error_type=error_type,
            fallback_used=fallback_used
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        print(f"🔴 HTTP Exception: {he.detail}")
        raise he
        
    except Exception as e:
        # Handle any unexpected errors
        print(f"🔴 Unexpected Error: {str(e)}")
        error_type = get_error_type(e)
        fallback_message = FALLBACK_MESSAGES.get(error_type, FALLBACK_MESSAGES["general_error"])
        
        # Try to generate fallback audio
        fallback_audio = generate_fallback_tts(fallback_message)
        
        return ChatResponse(
            success=False,
            message=f"Unexpected error occurred: {fallback_message}",
            audio_url=fallback_audio,
            transcript=user_message,
            llm_response=fallback_message,
            session_id=session_id,
            message_count=len(chat_sessions[session_id]),
            error_type=error_type,
            fallback_used=True
        )

@app.get("/agent/history/{session_id}", summary="Get Chat History", description="Retrieve conversation history for a session")
async def get_chat_history(
    session_id: str = Path(..., description="Session ID to retrieve history for")
):
    """
    Get the conversation history for a specific session.
    
    - **session_id**: The session identifier
    """
    history = chat_sessions.get(session_id, [])
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": history,
        "max_history": MAX_HISTORY_MESSAGES
    }

@app.delete("/agent/history/{session_id}", summary="Clear Chat History", description="Clear conversation history for a session")
async def clear_chat_history(
    session_id: str = Path(..., description="Session ID to clear history for")
):
    """
    Clear the conversation history for a specific session.
    
    - **session_id**: The session identifier
    """
    if session_id in chat_sessions:
        message_count = len(chat_sessions[session_id])
        del chat_sessions[session_id]
        return {
            "success": True,
            "message": f"Cleared {message_count} messages from session {session_id}",
            "session_id": session_id
        }
    else:
        return {
            "success": True,
            "message": "Session not found or already empty",
            "session_id": session_id
        }

@app.get("/agent/sessions", summary="List Active Sessions", description="Get list of all active chat sessions")
async def list_sessions():
    """
    Get a list of all active chat sessions.
    """
    sessions = []
    for session_id, messages in chat_sessions.items():
        if messages:
            sessions.append({
                "session_id": session_id,
                "message_count": len(messages),
                "last_message_time": messages[-1].get("timestamp") if messages else None,
                "first_message_time": messages[0].get("timestamp") if messages else None
            })
    
    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    else:
        raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint to verify API configuration"""
    return {
        "status": "healthy",
        "message": "Conversational AI Assistant with Memory is running!",
        "api_key_configured": bool(MURF_API_KEY),
        "sdk_initialized": bool(murf_client),
        "assemblyai_configured": bool(ASSEMBLYAI_API_KEY),
        "assemblyai_initialized": bool(aai_transcriber),
        "gemini_configured": bool(GEMINI_API_KEY),
        "gemini_initialized": bool(gemini_client),
        "active_sessions": len(chat_sessions),
        "total_messages": sum(len(msgs) for msgs in chat_sessions.values()),
        "features": [
            "Text-to-Speech generation",
            "Voice recording (Echo Bot)",
            "Audio file upload",
            "Audio transcription",
            "LLM query with Gemini",
            "Conversational chat with memory",
            "Session-based history",
            "Echo with Murf voice",
            "In-browser audio player",
            "Multiple voice options",
            "Volume and playback controls"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
