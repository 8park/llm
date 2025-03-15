import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# MPS fallback 설정
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

device = torch.device("cpu")
print(f"사용 디바이스: {device}")

model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

def translate(text, src_lang="eng_Latn", tgt_lang="kor_Hang"):
    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)
    print(f"Target Language ID for {tgt_lang}: {tgt_lang_id}")

    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(device)
    translated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tgt_lang_id,
        max_length=512
    )
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text

# 테스트 실행
src_text = "This is a test sentence for translation of academic papers."
translated = translate(src_text)
print("번역 결과:", translated)