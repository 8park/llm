# pip install transformers torch pymupdf pillow reportlab

import os

if not os.path.exists("static"):
    os.makedirs("static")

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from tkinter import Tk, filedialog
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Meta LLM (NLLB) 모델 로드 (예: facebook/nllb-200-distilled-600M)
device = torch.device("cpu")  # 안정성을 위해 CPU 사용 (필요에 따라 "mps" 또는 "cuda"로 변경)
model_name = "facebook/nllb-200-distilled-600M"
tokenizer_nllb = AutoTokenizer.from_pretrained(model_name)
model_nllb = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)


def translate_text(text, src_lang="eng_Latn", tgt_lang="kor_Hang"):
    """
    입력 텍스트를 Meta NLLB 모델을 사용해 번역합니다.
    영어 -> 한국어 번역 (원하는 언어 코드로 변경 가능)
    """
    inputs = tokenizer_nllb(text, return_tensors="pt", truncation=True).to(device)
    # 한국어 코드: "kor_Hang"
    tgt_lang_id = tokenizer_nllb.convert_tokens_to_ids(tgt_lang)
    translated_tokens = model_nllb.generate(
        **inputs,
        forced_bos_token_id=tgt_lang_id,
        max_length=512
    )
    translated_text = tokenizer_nllb.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text


def create_translated_pdf(original_pdf_path, output_pdf_path):
    """
    원본 PDF의 각 페이지에서 텍스트 블록을 추출해 번역하고,
    ReportLab을 사용해 흰색 배경 위에 번역된 텍스트만 재삽입하는 방식으로
    새로운 PDF를 생성합니다.
    """
    # 원본 PDF 열기
    doc = fitz.open(original_pdf_path)
    c = canvas.Canvas(output_pdf_path)

    for i, page in enumerate(doc):
        page_rect = page.rect
        width, height = page_rect.width, page_rect.height
        c.setPageSize((width, height))

        # 흰색 배경 채우기
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, width, height, fill=1)

        # 텍스트 블록 추출 ("blocks" 형식)
        blocks = page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, _, _ = b
            if text.strip():
                # Meta NLLB로 번역
                translated = translate_text(text)
                # ReportLab 좌표 변환 (PyMuPDF는 좌측 상단, ReportLab은 좌측 하단 기준)
                new_y = height - y1
                c.setFont("Helvetica", 10)
                c.drawString(x0, new_y, translated)

        c.showPage()

    c.save()
    print(f"번역된 PDF가 생성되었습니다: {output_pdf_path}")


def main():
    # tkinter GUI로 파일 선택
    root = Tk()
    root.withdraw()  # 메인 창 숨김
    original_pdf = filedialog.askopenfilename(
        title="원본 PDF 파일 선택",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not original_pdf:
        print("파일이 선택되지 않았습니다.")
        return

    # 원본 파일 이름에 "_kr" 접미사를 추가하여 출력 파일명 생성
    base, ext = os.path.splitext(original_pdf)
    output_pdf = base + "_kr" + ext

    print(f"선택된 PDF: {original_pdf}")
    print(f"번역된 PDF 저장 경로: {output_pdf}")

    # PDF 번역 및 생성
    create_translated_pdf(original_pdf, output_pdf)


if __name__ == "__main__":
    main()