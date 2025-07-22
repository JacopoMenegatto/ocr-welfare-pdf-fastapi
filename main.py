from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import fitz
import io
from PIL import Image
import pytesseract
from rules import valida_pratica_scuola_unicredit

app = FastAPI()

# Permettiamo richieste da FlutterFlow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Risposta(BaseModel):
    pratica_valida: bool
    errori: list

@app.post("/check_pratica_scuola", response_model=Risposta)
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
    # 🔍 OCR da PDF
    pdf_bytes = await file.read()
    doc = fitz.open("pdf", pdf_bytes)
    testo = ""
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        testo += pytesseract.image_to_string(img, lang="ita")

    testo = testo.lower()

    # Stima data e importo (semplice)
    data_pagamento = ""
    importo_pagato = 0.0
    for riga in testo.splitlines():
        if "202" in riga:
            data_pagamento = riga
        if "," in riga or "." in riga:
            try:
                importo_pagato = float(riga.replace("€", "").replace(",", ".").strip())
            except:
                continue

    # Valutazione
    dati = {
        "contanti": contanti,
        "causale": causale.lower(),
        "anno": anno,
        "importo_richiesto": importo_richiesto,
        "importo_pagato": importo_pagato,
        "data_pagamento": data_pagamento
    }

    errori = valida_pratica_scuola_unicredit(dati)
    return Risposta(pratica_valida=len(errori) == 0, errori=errori)
