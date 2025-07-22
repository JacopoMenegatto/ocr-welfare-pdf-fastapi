from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io

app = FastAPI()

# CORS per FlutterFlow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puoi restringerlo se vuoi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckResult(BaseModel):
    valid: bool
    reason: Optional[str] = None

@app.post("/check_pratica", response_model=CheckResult)
async def check_pratica(
    nome: str = Form(...),
    cognome: str = Form(...),
    codice_fiscale: str = Form(...),
    anno: int = Form(...),
    causale: str = Form(...),
    importo_richiesto: float = Form(...),
    contanti: bool = Form(...),
    file: UploadFile = File(...)
):
    # ✅ Step 1: leggi PDF e fai OCR
    text = ""
    pdf_bytes = await file.read()
    doc = fitz.open("pdf", pdf_bytes)
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img, lang="ita")

    # ✅ Step 2: estrai i dati OCR (grezzo, da migliorare)
    text = text.lower()
    if "contanti" in text or contanti:
        return CheckResult(valid=False, reason="Pagamento in contanti non ammesso")

    if "2022" in text:
        if anno == 2025:
            return CheckResult(valid=False, reason="Data non valida per il rimborso")

    if importo_richiesto > 10000:  # placeholder temporaneo
        return CheckResult(valid=False, reason="Importo richiesto eccessivo")

    if causale not in ["tasse scolastiche", "retta e quota di iscrizione", "mensa", "libri", "pre e post scuola", "gite scolastiche"]:
        return CheckResult(valid=False, reason="Causale non valida")

    # ✅ tutto ok
    return CheckResult(valid=True)
