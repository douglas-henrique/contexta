from pypdf import PdfReader


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() for page in reader.pages]
    return "\n".join(pages)
