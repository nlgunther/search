import zipfile
import json
import re
from abc import ABC, abstractmethod
from xml.etree import ElementTree

class BaseReader(ABC):
    @abstractmethod
    def read(self, filepath: str) -> str:
        """Read file and return plain text content."""
        pass

class ZipXmlReader(BaseReader):
    xml_filename = ""
    tag_name = ""
    namespace = ""

    def read(self, filepath: str) -> str:
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                with z.open(self.xml_filename) as f:
                    tree = ElementTree.parse(f)
                    tag = f"{{{self.namespace}}}{self.tag_name}" if self.namespace else self.tag_name
                    return " ".join(node.text for node in tree.iter(tag) if node.text)
        except Exception:
            return ""

class ODTReader(ZipXmlReader):
    xml_filename = 'content.xml'
    tag_name = 'p'
    namespace = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'

class DocxReader(ZipXmlReader):
    xml_filename = 'word/document.xml'
    tag_name = 't'
    namespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

class JupyterReader(BaseReader):
    def read(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                texts = []
                for cell in data.get('cells', []):
                    src = cell.get('source', [])
                    content = "".join(src) if isinstance(src, list) else str(src)
                    texts.append(content)
                return "\n".join(texts)
        except Exception:
            return ""

class PDFReader(BaseReader):
    def read(self, filepath: str) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            return " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

class ExcelReader(BaseReader):
    def read(self, filepath: str) -> str:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
            text_parts = []
            for sheet in wb:
                for row in sheet.iter_rows(values_only=True):
                    text_parts.append(" ".join(str(c) for c in row if c is not None))
            return "\n".join(text_parts)
        except Exception:
            return ""

READER_REGISTRY = {
    '.odt': ODTReader,
    '.docx': DocxReader,
    '.ipynb': JupyterReader,
    '.pdf': PDFReader,
    '.xlsx': ExcelReader,
    '.ods': ExcelReader
}
