from smolagents import LiteLLMModel
import json

# Initialize once (global)
ollama_model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",
    api_base="http://127.0.0.1:11434",
    num_ctx=2048,
)


def run_pipeline_with_llm(raw_texts, raw_tokens):
    """
    Stepwise LLM-based pipeline:
    1. Normalization - fix OCR errors, map to numeric values
    2. Classification - assign context labels to numbers
    3. Final Output - attach currency and source info
    Returns a dict with all 3 stages
    """
    pipeline_output = {}

    try:
        # ------------------- Step 1: Normalization -------------------
        prompt_norm = f"""
        You are a financial document parser.
        Given OCR output (raw lines + numeric tokens), return clean numeric values only.

        OCR Texts:
        {raw_texts}

        Extracted Tokens:
        {raw_tokens}

        Tasks:
        1. Correct OCR mistakes in numbers (O→0, l→1, etc.).
        2. Return JSON ONLY in this format:
        {{
            "normalized_amounts": [1200, 1000, 200, 10],
            "normalization_confidence": 0.82
        }}
        """

        messages_norm = [{"role": "user", "content": [{"type": "text", "text": prompt_norm}]}]
        raw_resp_norm = ollama_model(messages_norm)

        # Extract content
        #print('raw:',raw_resp_norm)
        resp_text_norm = getattr(raw_resp_norm, "content", str(raw_resp_norm))
        start, end = resp_text_norm.find("{"), resp_text_norm.rfind("}") + 1
        step1 = json.loads(resp_text_norm[start:end])
        print("\n=== Step 1: Normalization ===")
        print(step1)
        pipeline_output["normalization"] = step1

        # ------------------- Step 2: Classification -------------------
        prompt_class = f"""
        You are a financial document parser.
        Given OCR texts and normalized amounts, classify each number into its context.

        OCR Texts:
        {raw_texts}

        Normalized Amounts:
        {step1['normalized_amounts']}

        Tasks:
        1. Map each number to total_bill, paid, due, discount, or unknown.
        2. Return JSON ONLY in this format:
        {{
            "amounts": [
                {{"type":"total_bill","value":1200}},
                {{"type":"paid","value":1000}},
                {{"type":"due","value":200}},
                {{"type":"discount","value":10}}
            ],
            "confidence": 0.80
        }}
        """

        messages_class = [{"role": "user", "content": [{"type": "text", "text": prompt_class}]}]
        raw_resp_class = ollama_model(messages_class)
        resp_text_class = getattr(raw_resp_class, "content", str(raw_resp_class))
        start, end = resp_text_class.find("{"), resp_text_class.rfind("}") + 1
        step2 = json.loads(resp_text_class[start:end])
        print("\n=== Step 2: Classification ===")
        print(step2)
        pipeline_output["classification"] = step2

        # ------------------- Step 3: Final Output -------------------
        prompt_final = f"""
        You are a financial document parser.
        Given OCR texts and classified amounts, attach currency and source.

        OCR Texts:
        {raw_texts}

        Classified Amounts:
        {step2['amounts']}

        Tasks:
        1. Add currency (default INR if not present).
        2. Include source text for each number.
        3. Give little Summary on findings.
        4. Return JSON ONLY in this format:
        {{
            "currency": "INR",
            "amounts": [
                {{"type":"total_bill","value":1200,"source":"text: 'Total: INR 1200'"}},
                {{"type":"paid","value":1000,"source":"text: 'Paid: 1000'"}},
                {{"type":"due","value":200,"source":"text: 'Due: 200'"}},
                {{"type":"discount","value":10,"source":"text: 'discount': 10'"}}
            ],
            "summary":"The total bill is INR 1200 with 10% discount, person paid INR 1000 and remaining due is INR 200"
            "status":"ok"
        }}
        """

        messages_final = [{"role": "user", "content": [{"type": "text", "text": prompt_final}]}]
        raw_resp_final = ollama_model(messages_final)
        print(raw_resp_final)
        resp_text_final = getattr(raw_resp_final, "content", str(raw_resp_final))
        start, end = resp_text_final.find("{"), resp_text_final.rfind("}") + 1
        step3 = json.loads(resp_text_final[start:end])
        print("\n=== Step 3: Final Output ===")
        print(step3)
        pipeline_output["final"] = step3

        return pipeline_output

    except Exception as e:
        print("\n❌ Exception in run_pipeline_with_llm:", e)
        return {"normalization": {}, "classification": {}, "final": {}, "error": str(e)}
