import fitz  # PyMuPDF
import tempfile
import os

_ocr_engine = None


def _get_ocr():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_engine = PaddleOCR(use_angle_cls=True, lang="es", show_log=False)
        except ImportError:
            raise RuntimeError("PaddleOCR no disponible en este entorno. Usa la opción de texto manual.")
    return _ocr_engine


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        doc = fitz.open(tmp_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        if text.strip():
            return text.strip()

        # PDF is scanned — use PaddleOCR page by page
        return _ocr_scanned_pdf(tmp_path)
    finally:
        os.unlink(tmp_path)


def extract_text_from_image(img_bytes: bytes, suffix: str = ".png") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name
    try:
        return _ocr_image(tmp_path)
    finally:
        os.unlink(tmp_path)


def _ocr_scanned_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    result_text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_tmp:
            pix.save(img_tmp.name)
            result_text += _ocr_image(img_tmp.name) + "\n"
            os.unlink(img_tmp.name)
    doc.close()
    return result_text.strip()


def _ocr_image(img_path: str) -> str:
    ocr = _get_ocr()
    result = ocr.ocr(img_path, cls=True)
    if not result or not result[0]:
        return ""
    return "\n".join(line[1][0] for line in result[0] if line)
