# modules/ocr_reader.py
import cv2
import pytesseract
import config

def perform_ocr(image_roi):
    """
    Recebe uma imagem JÁ CORTADA da região de interesse (ROI),
    realiza o pré-processamento e o OCR, retornando o texto e a imagem processada.
    """
    # Pré-processamento
    gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Executa o OCR na imagem final limpa
    text = pytesseract.image_to_string(closing, config=config.TESS_CONFIG)
    
    # Limpa o texto resultante
    cleaned_text = "".join(filter(str.isalnum, text.upper()))
    
    # Retorna tanto o texto lido quanto a imagem final para depuração
    return cleaned_text, closing