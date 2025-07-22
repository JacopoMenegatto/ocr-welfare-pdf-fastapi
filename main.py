from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io

app = FastAPI()

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    pdf = fitz.open(stream=contents, filetype="pdf")

    extracted_text = ""
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        pix = page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(image, lang="ita")
        extracted_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"

    return JSONResponse(content={"text": extracted_text})
