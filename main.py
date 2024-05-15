from fastapi import FastAPI, HTTPException, Request, File, UploadFile

from pydantic import BaseModel
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from gtts import gTTS
import os
from deep_translator import GoogleTranslator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import speech_recognition as sr
from fastapi.responses import FileResponse
import io


app = FastAPI()
app.mount("/transcripts", StaticFiles(directory="transcripts"), name="transcripts")
r = sr.Recognizer()

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='0.0.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add the origin where your frontend is hosted
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


@app.post("/audio-to-text/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read the contents of the uploaded audio file
        contents = await file.read()
       
        # Convert audio data to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(contents)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        print(text)
        translated = GoogleTranslator(source='auto', target='ta').translate(text)
        print("Translated to Tamil:", translated)
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")

        # Construct the file name with the timestamp
        file_name = f"Tamil-Audio_{timestamp_str}.mp3"
        file_path = os.path.join("./transcripts/", file_name)

        # Convert the translated text to speech and save as an MP3 file
        tts = gTTS(text=translated, lang='ta')
        tts.save(file_path)

        print(f"Translated audio saved to '{file_name}'")

        return {"status": "success", "file_name": f"/transcripts/{file_name}"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/recognize_and_translate/")
async def recognize_and_translate(request: Request):
    try:
        text_input = await request.json()
        text = text_input['text']
        # Translate the text to Tamil
        translated = GoogleTranslator(source='auto', target='ta').translate(text)
        print("Translated to Tamil:", translated)

        # Get the current timestamp
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")

        # Construct the file name with the timestamp
        file_name = f"Tamil-Audio_{timestamp_str}.mp3"
        file_path = os.path.join("./transcripts/", file_name)

        # Convert the translated text to speech and save as an MP3 file
        tts = gTTS(text=translated, lang='ta')
        tts.save(file_path)

        print(f"Translated audio saved to '{file_name}'")

        return {"status": "success", "file_name": f"/transcripts/{file_name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
