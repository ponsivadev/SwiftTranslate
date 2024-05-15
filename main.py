from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from gtts import gTTS
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Add the origin where your frontend is hosted
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
# Load service account key file
credentials = service_account.Credentials.from_service_account_file('service.json')

# Initialize Google Cloud Translation client with credentials
translate_client = translate.Client(credentials=credentials)

class TranslationRequest(BaseModel):
    text: str

@app.post("/translate/")
async def translate_text(req: TranslationRequest):
    english_text = req.text

    # Translate English text to Tamil
    translated = translate_client.translate(
        english_text, target_language='ta')  # 'ta' is the language code for Tamil
    tamil_text = translated['translatedText']

    # Convert translated Tamil text to speech
    tts = gTTS(text=tamil_text, lang='ta')
    tts.save("translated_text.mp3")

    return {"translatedText": tamil_text}

@app.get("/play/")
async def play_audio():
    return FileResponse("translated_text.mp3", media_type="audio/mpeg")
