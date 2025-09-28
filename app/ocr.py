from easyocr import Reader
from typing import List, Tuple
from .utils import clean_ocr_token, guess_currency
import numpy as np
import cv2


# instantiate EasyOCR reader lazily to avoid heavy import cost at module import
_reader = None


def get_reader(lang_list: List[str] = ["en"]):
    global _reader
    if _reader is None:
        _reader = Reader(lang_list, gpu=False) # set gpu=True if available
    return _reader




def run_ocr_image(image_bytes: bytes, lang_list=["en"]) -> Tuple[List[str], float, str]:
    reader = get_reader(lang_list)
    results = reader.readtext(image_bytes, detail=1)

    extracted = []
    confidences = []
    for bbox, text, conf in results:
        if text and text.strip():
            extracted.append(text.strip())
            confidences.append(conf)

    avg_conf = float(np.mean(confidences)) if confidences else 0.0

    # Heuristic: currency
    currency = guess_currency(" ".join(extracted))

    # Instead of regex-breaking tokens, just return full OCR lines
    raw_tokens = extracted

    return raw_tokens, avg_conf, currency


def run_ocr_debug(image_bytes: bytes, lang_list=["en"], save_path="debug_output.jpg"):
    """
    Run OCR and save an image with bounding boxes + detected text for debugging.
    Only return text + confidence (no bbox in console).
    """
    # Convert image bytes to array
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    reader = get_reader(lang_list)
    results = reader.readtext(img, detail=1)

    extracted = []
    for bbox, text, conf in results:
        # Draw bounding box on the debug image
        pts = np.array(bbox, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        # Put text + confidence on the debug image
        x, y = pts[0][0]
        cv2.putText(img, f"{text} ({conf:.2f})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Save only text + confidence in results
        extracted.append({"text": text.strip(), "confidence": float(conf)})

    cv2.imwrite(save_path, img)
    return extracted, save_path


# Example usage
# with open(r"C:\Users\Akash\Downloads\medtest.png", "rb") as f:
#     img_bytes = f.read()

# detected, out_path = run_ocr_debug(img_bytes, save_path="ocr_debug.jpg")
# print("OCR Detected Tokens:")
# for item in detected:
#     print(f"  - {item['text']} (conf: {item['confidence']:.2f})")
# print("Saved debug image:", out_path)

