import re
from typing import Tuple, Optional


CURRENCY_PATTERNS = [r"\bINR\b", r"₹", r"\bRs\b", r"\bRs\.\b", r"\bRs:\b"]


DIGIT_FIX_MAP = {
'l': '1',
'I': '1',
'O': '0',
'o': '0',
'S': '5',
's': '5',
'|': '1'
}




def guess_currency(text: str) -> Optional[str]:
    for pat in CURRENCY_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            return "INR"
    return None




def clean_ocr_token(tok: str) -> str:
    # Basic character-level fixes
    fixed = ''.join(DIGIT_FIX_MAP.get(c, c) for c in tok)
    # Remove common separators and stray letters except percent and dot
    fixed = re.sub(r"[^0-9.%]", "", fixed)
    return fixed




def is_percent(tok: str) -> bool:
    return tok.strip().endswith('%')




def extract_numeric_value(tok: str) -> Optional[float]:
    t = tok.strip()
    if not t:
        return None
    try:
        if t.endswith('%'):
            return float(t[:-1])
    # remove commas
        t2 = t.replace(',', '')
        return float(t2)
    except Exception:
        return None