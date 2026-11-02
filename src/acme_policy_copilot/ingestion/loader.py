from pathlib import Path
from pypdf import PdfReader
import sys
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException


DATA_DIR = Path("data/raw")


def load_pdfs():
    documents = []
    try:
        pdf_files = list(DATA_DIR.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        for pdf_path in pdf_files:
            logger.info(f"Loading: {pdf_path.name}")
            reader = PdfReader(pdf_path)
            logger.debug(f"{pdf_path.name} contains {len(reader.pages)} pages")
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if not text.strip():
                    logger.warning(f"Empty page: {pdf_path.name}, page {page_number}")
                    continue

                documents.append({
                    "text": text,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_number
                    }
                })

        logger.info(f"Successfully loaded {len(documents)} pages")
        return documents

    except Exception as e:
        logger.error("Error while loading PDFs")
        raise RAGException(e, sys)

if __name__ == "__main__":
    documents = load_pdfs()
    print(f"Total documents: {len(documents)}")
    print(documents[0])