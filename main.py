from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import subprocess
import uuid
import os
from typing import Optional
import textgrid

app = FastAPI()

UPLOAD_DIR = "./uploads"
ALIGN_DIR = "./alignments"
DICT_PATH = "english.dict"  # Pre-trained MFA dictionary (download separately)
ACOUSTIC_MODEL = "english"  # Assumes downloaded via `mfa model download acoustic english`

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ALIGN_DIR, exist_ok=True)

@app.post("/align/")
async def align_audio(
    audio: UploadFile,
    transcript: str = Form(...),
    speaker_id: Optional[str] = Form(None)
):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    audio_path = os.path.join(session_dir, "audio.wav")
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    lab_path = os.path.join(session_dir, "audio.lab")
    with open(lab_path, "w", encoding="utf-8") as f:
        f.write(transcript.strip())

    align_cmd = [
        "mfa_align",
        session_dir,
        DICT_PATH,
        ACOUSTIC_MODEL,
        ALIGN_DIR,
        "--clean",
        "--overwrite"
    ]

    try:
        subprocess.run(align_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"error": "MFA alignment failed", "details": str(e)})

    tg_path = os.path.join(ALIGN_DIR, "audio", "audio.TextGrid")
    if not os.path.exists(tg_path):
        return JSONResponse(status_code=404, content={"error": "Alignment output not found"})

    try:
        tg = textgrid.TextGrid.fromFile(tg_path)
        word_tier = tg.getFirst("words")
        phone_tier = tg.getFirst("phones")

        total_words = len(word_tier)
        missing_words = sum(1 for interval in word_tier if interval.mark.strip() == "" or interval.mark.strip() == "sp")

        total_phones = len(phone_tier)
        missing_phones = sum(1 for p in phone_tier if p.mark.strip() == "" or p.mark.strip() in ["sp", "sil"])

        phone_accuracy = (total_phones - missing_phones) / total_phones if total_phones else 0

        if phone_accuracy >= 0.9:
            cefr = "C1"
            score = 8.0
        elif phone_accuracy >= 0.8:
            cefr = "B2"
            score = 6.5
        elif phone_accuracy >= 0.7:
            cefr = "B1"
            score = 5.5
        else:
            cefr = "A2 or below"
            score = 4.5

        result = {
            "pronunciation_score": round(score, 1),
            "cefr_estimate": cefr,
            "missing_words": missing_words,
            "total_words": total_words,
            "missing_phones": missing_phones,
            "total_phones": total_phones,
            "phoneme_accuracy": round(phone_accuracy, 2)
        }
        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to parse TextGrid", "details": str(e)})
