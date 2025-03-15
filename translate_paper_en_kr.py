import os
import fitz  # PyMuPDF
from tkinter import Tk, filedialog
from deep_translator import GoogleTranslator


def extract_text_from_pdf(pdf_path):
    """
    PDF의 모든 텍스트를 추출하여 한 줄의 문자열로 반환합니다.
    각 페이지의 텍스트 사이에는 공백을 추가하여 한 줄로 만듭니다.
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + " "
    # 연속된 공백은 하나의 공백으로 정리
    full_text = " ".join(full_text.split())
    return full_text


def translate_text_with_google(text, max_length=4000):
    """
    입력된 영어 텍스트를 4000자씩 청크로 나눈 후,
    deep_translator의 GoogleTranslator로 순차 번역하여 합쳐서 반환합니다.
    """
    # 4000자 기준으로 청크 분할
    chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"청크 {idx + 1}/{len(chunks)} 번역 중...")
        translated = GoogleTranslator(source='en', target='ko').translate(chunk)
        translated_chunks.append(translated)
    return "\n".join(translated_chunks)


def main():
    # 폴더 선택 GUI 열기
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="PDF 파일이 있는 폴더 선택")
    if not folder_path:
        print("폴더가 선택되지 않았습니다.")
        return

    # 결과를 저장할 서브 폴더 생성: 영어 txt, 한글 txt
    english_folder = os.path.join(folder_path, "영어txt")
    korean_folder = os.path.join(folder_path, "한글txt")
    os.makedirs(english_folder, exist_ok=True)
    os.makedirs(korean_folder, exist_ok=True)

    # 폴더 내의 모든 PDF 파일에 대해 처리
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"처리 중: {pdf_path}")
            extracted_text = extract_text_from_pdf(pdf_path)

            # 영어 텍스트 저장
            base, _ = os.path.splitext(filename)
            english_txt_path = os.path.join(english_folder, base + ".txt")
            with open(english_txt_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            print(f"영어 텍스트 저장: {english_txt_path}")

            # 전체 텍스트 번역
            translated_text = translate_text_with_google(extracted_text, max_length=4000)
            korean_txt_path = os.path.join(korean_folder, base + ".txt")
            with open(korean_txt_path, "w", encoding="utf-8") as f:
                f.write(translated_text)
            print(f"한글 텍스트 저장: {korean_txt_path}")


if __name__ == "__main__":
    main()