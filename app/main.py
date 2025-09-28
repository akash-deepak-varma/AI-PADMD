from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List
from .ocr import run_ocr_image
#from .schemas import OCRResponse, NormalizationResponse, ClassificationResponse, FinalResponse, GuardrailResponse
from .utils import guess_currency
from .config import settings
import io
import json
import numpy as np
from .llm_utils import run_pipeline_with_llm
import cv2

app = FastAPI(title="Amount Extractor API")


@app.get("/")
def root():
    return {"msg": "AI Medical OCR API running"}


# @app.post('/process_image')
# async def process_image(file: UploadFile = File(...)):
#     # read image bytes
#     try:
#         image_bytes = await file.read()
#     except Exception:
#         raise HTTPException(status_code=400, detail="failed to read image file")

#     # Step 1: OCR
#     raw_tokens, ocr_conf, currency_hint = run_ocr_image(image_bytes, lang_list=[settings.OCR_LANGS])
#     if not raw_tokens:
#         return JSONResponse(status_code=200, content={"status":"no_amounts_found","reason":"document too noisy"})

#     # Step 2: Normalize
#     normalized, norm_conf = normalize_tokens(raw_tokens)
#     if not normalized:
#         return JSONResponse(status_code=200, content={"status":"no_amounts_found","reason":"normalization failed"})

#     # Step 3: Classification
#     classified, class_conf = classify_amounts(raw_tokens, normalized)

#     # Step 4: Final assembly
#     amounts = []
#     for item in classified:
#         amounts.append({
#             "type": item.get('type', 'unknown'),
#             "value": item.get('value'),
#             "source": item.get('source') or "image_ocr"
#         })

#     final = {
#         "currency": currency_hint or "INR",
#         "amounts": amounts,
#         "status": "ok"
#     }
#     return JSONResponse(status_code=200, content=final)

@app.post("/process_image_stepwise")
async def process_image_stepwise(file: UploadFile = File(...)):
    image_bytes = await file.read()


    raw_tokens, conf, currency = run_ocr_image(image_bytes)
    ocr_output = {
        "stage": "ocr",
        "raw_tokens": raw_tokens,
        "currency_hint": currency,
        "confidence": conf
    }

    if conf < 0.3:
        print("Confidence is too low to proceed")
        return {
            "pipeline": [
                ocr_output,
            ],
            "problem":"confidence is too low cant proceed futher"
        }



    llm_pipeline_result = run_pipeline_with_llm(raw_tokens, raw_tokens)


    normalization_output = {
        "stage": "normalization",
        "normalized_amounts": llm_pipeline_result.get("normalization", {}).get("normalized_amounts", []),
        "normalization_confidence": llm_pipeline_result.get("normalization", {}).get("normalization_confidence", 0.9)
    }


    classification_output = {
        "stage": "classification",
        "amounts": llm_pipeline_result.get("classification", {}).get("amounts", []),
        "confidence": llm_pipeline_result.get("classification", {}).get("confidence", 0.9)
    }


    final_output = {
        "stage": "final",
        "currency": llm_pipeline_result.get("final", {}).get("currency", currency or "INR"),
        "amounts": llm_pipeline_result.get("final", {}).get("amounts", []),
        "summary": llm_pipeline_result.get("final", {}).get("summary", []),
        "status": llm_pipeline_result.get("final", {}).get("status", "ok")
    }


    return {
        "pipeline": [
            ocr_output,
            normalization_output,
            classification_output,
            final_output
        ]
    }




# @app.post('/process_text')
# async def process_text(text: str = Form(...)):
#     # For demo: accept raw text and run the same pipeline
#     raw_text = text
#     # Simple extraction from text using OCR step (simulate)
#     raw_tokens, ocr_conf, currency_hint = run_ocr_image(raw_text.encode('utf8'), lang_list=[settings.OCR_LANGS])
#     if not raw_tokens:
#         return JSONResponse(status_code=200, content={"status":"no_amounts_found","reason":"no numeric tokens"})
#     normalized, norm_conf = normalize_tokens(raw_tokens)
#     if not normalized:
#         return JSONResponse(status_code=200, content={"status":"no_amounts_found","reason":"normalization failed"})
#     classified, class_conf = classify_amounts(raw_tokens, normalized)
#     amounts = []
#     for item in classified:
#         amounts.append({
#             "type": item.get('type', 'unknown'),
#             "value": item.get('value'),
#             "source": item.get('source') or f"text: '{raw_text}'"
#         })
#     final = {"currency": currency_hint or "INR", "amounts": amounts, "status": "ok"}
#     return JSONResponse(status_code=200, content=final)