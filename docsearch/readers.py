"""
File readers for various document formats.

This module provides a registry of readers for different file types.
Each reader extracts text content and metadata from its supported format.

Supported formats:
- PDF (.pdf)
- Word (.docx, .doc)
- OpenDocument (.odt)
- Excel (.xlsx, .xls, .ods)
- Jupyter Notebooks (.ipynb)
- Markdown (.md)
- Plain text (.txt)
"""

import os
from pathlib import Path
from typing import Protocol, Dict, Type, Optional
from .models import ReadResult, ReadStatus, FileMetadata


class BaseReader(Protocol):
    """Protocol for file readers."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        """Check if this reader can read the file."""
        ...
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        """Read file and return result."""
        ...


class PDFReader:
    """Reader for PDF files."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.lower().endswith('.pdf')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        if not os.path.exists(filepath):
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.NOT_FOUND,
                error="File not found"
            )
        
        try:
            import pypdf
        except ImportError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.UNSUPPORTED_FORMAT,
                error="pypdf not installed. Install with: pip install pypdf"
            )
        
        try:
            with open(filepath, 'rb') as f:
                reader = pypdf.PdfReader(f)
                
                # Extract text
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text())
                text = '\n'.join(text_parts)
                
                # Extract metadata
                metadata = FileMetadata(
                    page_count=len(reader.pages),
                    author=reader.metadata.get('/Author'),
                    title=reader.metadata.get('/Title'),
                    file_size=os.path.getsize(filepath)
                )
                
                if not text.strip():
                    return ReadResult(
                        filepath=filepath,
                        status=ReadStatus.EMPTY_FILE,
                        error="PDF contains no extractable text"
                    )
                
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.SUCCESS,
                    text=text,
                    metadata=metadata
                )
                
        except pypdf.errors.PdfReadError as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.CORRUPT_FILE,
                error=f"Corrupt PDF: {str(e)}"
            )
        except PermissionError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.PERMISSION_DENIED,
                error="Permission denied"
            )
        except Exception as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error=f"Error reading PDF: {str(e)}"
            )


class DocxReader:
    """Reader for Word documents."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.lower().endswith('.docx')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        if not os.path.exists(filepath):
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.NOT_FOUND,
                error="File not found"
            )
        
        try:
            import docx
        except ImportError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.UNSUPPORTED_FORMAT,
                error="python-docx not installed. Install with: pip install python-docx"
            )
        
        try:
            doc = docx.Document(filepath)
            
            # Extract text
            text = '\n'.join(para.text for para in doc.paragraphs)
            
            # Extract metadata
            props = doc.core_properties
            metadata = FileMetadata(
                author=props.author,
                title=props.title,
                created_date=str(props.created) if props.created else None,
                modified_date=str(props.modified) if props.modified else None,
                file_size=os.path.getsize(filepath),
                word_count=len(text.split())
            )
            
            if not text.strip():
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.EMPTY_FILE,
                    error="Document contains no text"
                )
            
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.SUCCESS,
                text=text,
                metadata=metadata
            )
            
        except PermissionError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.PERMISSION_DENIED,
                error="Permission denied"
            )
        except Exception as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error=f"Error reading DOCX: {str(e)}"
            )


class OdtReader:
    """Reader for OpenDocument Text (.odt) files."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.lower().endswith('.odt')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        if not os.path.exists(filepath):
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.NOT_FOUND,
                error="File not found"
            )
        
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            # ODT files are ZIP archives containing XML
            with zipfile.ZipFile(filepath, 'r') as odt_zip:
                # Extract content.xml which contains the document text
                content_xml = odt_zip.read('content.xml')
            
            # Parse XML and extract text
            root = ET.fromstring(content_xml)
            
            # ODT uses namespaces - need to handle them
            namespaces = {
                'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
            }
            
            # Extract all text elements
            text_parts = []
            for elem in root.iter():
                # Get text from text:p (paragraphs) and text:h (headings)
                if elem.tag.endswith('}p') or elem.tag.endswith('}h'):
                    if elem.text:
                        text_parts.append(elem.text)
                    # Also get text from child elements
                    for child in elem.iter():
                        if child.text and child != elem:
                            text_parts.append(child.text)
                        if child.tail:
                            text_parts.append(child.tail)
            
            text = '\n'.join(text_parts)
            
            if not text.strip():
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.EMPTY_FILE,
                    error="File is empty"
                )
            
            metadata = FileMetadata(
                file_size=os.path.getsize(filepath),
                word_count=len(text.split())
            )
            
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.SUCCESS,
                text=text,
                metadata=metadata
            )
            
        except zipfile.BadZipFile:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error="Invalid ODT file (not a valid ZIP archive)"
            )
        except KeyError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error="Invalid ODT file (missing content.xml)"
            )
        except Exception as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error=f"Error reading ODT: {str(e)}"
            )


class MarkdownReader:
    """Reader for Markdown and plain text files."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        ext = filepath.lower()
        return ext.endswith('.md') or ext.endswith('.txt')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        if not os.path.exists(filepath):
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.NOT_FOUND,
                error="File not found"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            metadata = FileMetadata(
                file_size=os.path.getsize(filepath),
                word_count=len(text.split())
            )
            
            if not text.strip():
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.EMPTY_FILE,
                    error="File is empty"
                )
            
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.SUCCESS,
                text=text,
                metadata=metadata
            )
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    text = f.read()
                metadata = FileMetadata(file_size=os.path.getsize(filepath))
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.SUCCESS,
                    text=text,
                    metadata=metadata
                )
            except Exception as e:
                return ReadResult(
                    filepath=filepath,
                    status=ReadStatus.READ_ERROR,
                    error=f"Encoding error: {str(e)}"
                )
        except PermissionError:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.PERMISSION_DENIED,
                error="Permission denied"
            )
        except Exception as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error=f"Error reading file: {str(e)}"
            )


# Reader Registry
READER_REGISTRY: Dict[str, Type[BaseReader]] = {
    '.pdf': PDFReader,
    '.docx': DocxReader,
    '.odt': OdtReader,  # OpenDocument Text
    '.md': MarkdownReader,
    '.txt': MarkdownReader,
    '.csv': MarkdownReader,  # CSV files are plain text
    '.xml': MarkdownReader,  # XML files are plain text
    '.json': MarkdownReader,  # JSON files are plain text
    '.html': MarkdownReader,  # HTML files are plain text
    '.htm': MarkdownReader,   # HTML files are plain text
    '.log': MarkdownReader,   # Log files are plain text
    '.yml': MarkdownReader,   # YAML files are plain text
    '.yaml': MarkdownReader,  # YAML files are plain text
    # Code files (all plain text)
    '.py': MarkdownReader,    # Python
    '.js': MarkdownReader,    # JavaScript
    '.ts': MarkdownReader,    # TypeScript
    '.java': MarkdownReader,  # Java
    '.c': MarkdownReader,     # C
    '.cpp': MarkdownReader,   # C++
    '.h': MarkdownReader,     # C/C++ headers
    '.cs': MarkdownReader,    # C#
    '.go': MarkdownReader,    # Go
    '.rs': MarkdownReader,    # Rust
    '.rb': MarkdownReader,    # Ruby
    '.php': MarkdownReader,   # PHP
    '.swift': MarkdownReader, # Swift
    '.kt': MarkdownReader,    # Kotlin
    '.r': MarkdownReader,     # R
    '.sql': MarkdownReader,   # SQL
    '.sh': MarkdownReader,    # Shell scripts
    '.bash': MarkdownReader,  # Bash scripts
    '.ps1': MarkdownReader,   # PowerShell
    '.bat': MarkdownReader,   # Batch files
    # Markup/styling
    '.css': MarkdownReader,   # CSS
    '.scss': MarkdownReader,  # SCSS
    '.sass': MarkdownReader,  # SASS
    '.less': MarkdownReader,  # LESS
    '.xsl': MarkdownReader,   # XSL
    '.xslt': MarkdownReader,  # XSLT
    # Config files
    '.ini': MarkdownReader,   # INI config
    '.conf': MarkdownReader,  # Config files
    '.cfg': MarkdownReader,   # Config files
    '.toml': MarkdownReader,  # TOML
    '.env': MarkdownReader,   # Environment files
    # Other text formats
    '.rst': MarkdownReader,   # ReStructuredText
    '.tex': MarkdownReader,   # LaTeX
}


def get_reader(filepath: str) -> Optional[Type[BaseReader]]:
    """Get appropriate reader for file."""
    ext = Path(filepath).suffix.lower()
    return READER_REGISTRY.get(ext)


def read_file(filepath: str) -> ReadResult:
    """
    Read a file and return result.
    
    Args:
        filepath: Path to file
        
    Returns:
        ReadResult with status, text, and metadata
        
    Examples:
        >>> result = read_file("document.pdf")
        >>> if result.ok:
        ...     print(result.text)
        ...     print(f"Pages: {result.metadata.page_count}")
    """
    reader = get_reader(filepath)
    if not reader:
        ext = Path(filepath).suffix
        return ReadResult(
            filepath=filepath,
            status=ReadStatus.UNSUPPORTED_FORMAT,
            error=f"Unsupported file format: {ext}"
        )
    
    return reader.read(filepath)


def read_file_preview(filepath: str, n_tokens: int = 250) -> ReadResult:
    """
    Read first N tokens from file (efficient for previews).
    
    Args:
        filepath: Path to file
        n_tokens: Number of tokens to extract
        
    Returns:
        ReadResult with truncated text
        
    Examples:
        >>> result = read_file_preview("large_doc.pdf", n_tokens=100)
        >>> print(result.text[:200])
    """
    result = read_file(filepath)
    
    if result.ok and n_tokens > 0:
        tokens = result.text.split()[:n_tokens]
        result.text = ' '.join(tokens)
    
    return result


def get_supported_formats() -> Dict[str, str]:
    """Get dictionary of supported formats and their readers."""
    formats = {}
    for ext, reader_class in READER_REGISTRY.items():
        formats[ext] = reader_class.__name__
    return formats
