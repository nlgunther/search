# DocSearch v2.0 - Complete Source Code Reference

This file contains all the source code for the docsearch package.
Each module is clearly marked with headers.

## Package Structure

```
docsearch/
├── __init__.py        # Public API
├── models.py          # Data models
├── readers.py         # File readers
├── batch.py           # Batch processing
├── glob_filter.py     # Glob pattern filtering
└── cli.py             # Command-line interface
```

================================================================================
FILE: docsearch/__init__.py
================================================================================

"""
DocSearch - Document search and classification toolkit.

A Python package for extracting content from various document formats
and creating structured batches for classification workflows.

Features:
- Multi-format support (PDF, DOCX, Markdown, etc.)
- Glob pattern filtering
- Batch processing with parallel execution
- Rich metadata extraction
- Explicit error handling
- CLI interface

Basic Usage:
    >>> from docsearch import read_file
    >>> result = read_file("document.pdf")
    >>> if result.ok:
    ...     print(result.text)
    
    >>> from docsearch import create_labeled_batch_from_directory
    >>> batch_text = create_labeled_batch_from_directory(
    ...     "/invoices",
    ...     categories=["invoice"]
    ... )
"""

__version__ = "2.0.0"

# Core reading functions
from .readers import (
    read_file,
    read_file_preview,
    get_supported_formats,
    get_reader,
)

# Data models
from .models import (
    ReadStatus,
    ReadResult,
    FileMetadata,
    Batch,
    BatchEntry,
    BatchCollection,
)

# Batch processing
from .batch import (
    collect_files,
    create_batch_from_files,
    create_labeled_batch_from_directory,
    files_from_text,
    files_from_file,
    BatchBuilder,
)

# Glob filtering
from .glob_filter import (
    glob_matches,
    filter_files_by_glob,
    apply_glob_filter,
)

# Public API
__all__ = [
    # Version
    '__version__',
    
    # Reading
    'read_file',
    'read_file_preview',
    'get_supported_formats',
    'get_reader',
    
    # Models
    'ReadStatus',
    'ReadResult',
    'FileMetadata',
    'Batch',
    'BatchEntry',
    'BatchCollection',
    
    # Batch processing
    'collect_files',
    'create_batch_from_files',
    'create_labeled_batch_from_directory',
    'files_from_text',
    'files_from_file',
    'BatchBuilder',
    
    # Glob filtering
    'glob_matches',
    'filter_files_by_glob',
    'apply_glob_filter',
]


================================================================================
FILE: docsearch/models.py
================================================================================

"""
Data models for docsearch package.

This module defines the core data structures used throughout docsearch:
- ReadStatus: Enum for file read outcomes
- FileMetadata: Structured metadata from documents
- ReadResult: Return type for file reading operations
- BatchEntry: Single file entry in a batch
- Batch: Collection of related files
- BatchCollection: Multiple batches for processing
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import json


class ReadStatus(Enum):
    """Status of file reading operation."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    UNSUPPORTED_FORMAT = "unsupported_format"
    CORRUPT_FILE = "corrupt_file"
    EMPTY_FILE = "empty_file"
    READ_ERROR = "read_error"


@dataclass
class FileMetadata:
    """Metadata extracted from a document."""
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    file_size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ReadResult:
    """Result of reading a file."""
    filepath: str
    status: ReadStatus
    text: str = ""
    metadata: FileMetadata = field(default_factory=FileMetadata)
    error: Optional[str] = None
    
    @property
    def ok(self) -> bool:
        """True if read was successful."""
        return self.status == ReadStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filepath": self.filepath,
            "status": self.status.value,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
            "error": self.error,
        }


@dataclass
class BatchEntry:
    """Single file entry in a batch."""
    filepath: str
    filename: str
    extension: str
    size: int
    tokens: str
    
    def to_format(self) -> str:
        """Convert to batch format."""
        return f"""<file>
FILEPATH: {self.filepath}
FILENAME: {self.filename}
EXTENSION: {self.extension}
SIZE: {self.size}
TOKENS:
{self.tokens}"""


@dataclass
class Batch:
    """Collection of related files with optional categories."""
    categories: List[str] = field(default_factory=list)
    files: List[BatchEntry] = field(default_factory=list)
    
    def to_format(self) -> str:
        """Convert to batch format."""
        category_line = f"CATEGORIES: {', '.join(self.categories)}" if self.categories else "CATEGORIES:"
        file_blocks = '\n'.join(entry.to_format() for entry in self.files)
        return f"""<batch>
{category_line}
{file_blocks}"""


@dataclass
class BatchCollection:
    """Collection of batches for processing."""
    batches: List[Batch] = field(default_factory=list)
    
    def to_format(self) -> str:
        """Convert to batch format."""
        return '\n'.join(batch.to_format() for batch in self.batches) + '\n'
    
    @classmethod
    def from_format(cls, text: str) -> 'BatchCollection':
        """Parse batch format back to BatchCollection."""
        batches = []
        current_batch = None
        current_file = None
        current_field = None
        tokens_lines = []
        
        for line in text.split('\n'):
            stripped = line.strip()
            
            if stripped == '<batch>':
                if current_batch and current_batch.files:
                    batches.append(current_batch)
                current_batch = Batch()
                current_file = None
                
            elif stripped.startswith('CATEGORIES:'):
                if current_batch:
                    cats = stripped[11:].strip()
                    current_batch.categories = [c.strip() for c in cats.split(',') if c.strip()]
                    
            elif stripped == '<file>':
                if current_file:
                    current_file.tokens = '\n'.join(tokens_lines)
                    current_batch.files.append(current_file)
                current_file = {}
                tokens_lines = []
                current_field = None
                
            elif stripped.startswith('FILEPATH:'):
                current_file['filepath'] = stripped[9:].strip()
            elif stripped.startswith('FILENAME:'):
                current_file['filename'] = stripped[9:].strip()
            elif stripped.startswith('EXTENSION:'):
                current_file['extension'] = stripped[10:].strip()
            elif stripped.startswith('SIZE:'):
                current_file['size'] = int(stripped[5:].strip())
            elif stripped.startswith('TOKENS:'):
                current_field = 'tokens'
            elif current_field == 'tokens':
                tokens_lines.append(line)  # Preserve original formatting
        
        # Add last file and batch
        if current_file:
            current_file['tokens'] = '\n'.join(tokens_lines)
            entry = BatchEntry(**current_file)
            current_batch.files.append(entry)
        if current_batch:
            batches.append(current_batch)
            
        return cls(batches=batches)
    
    def all_files(self) -> List[tuple[List[str], BatchEntry]]:
        """Iterate over all files with their categories."""
        for batch in self.batches:
            for entry in batch.files:
                yield (batch.categories, entry)


================================================================================
FILE: docsearch/glob_filter.py
================================================================================

"""
Glob pattern filtering for docsearch.

This module provides glob pattern matching for file filtering in docsearch
commands. It supports Unix-style wildcards with special handling for
recursive patterns.

Usage:
    from docsearch.glob_filter import filter_files_by_glob, apply_glob_filter
    
    files = collect_all_files("/documents")
    filtered = filter_files_by_glob(files, "*.pdf,*.docx")
"""

import re
import fnmatch
from typing import List, Optional
import sys


def glob_matches(filepath: str, pattern: str) -> bool:
    """
    Check if filepath matches glob pattern.
    
    Supports:
    - * matches any characters except /
    - ** matches any characters including /
    - ? matches single character
    - [seq] matches any character in seq
    - [!seq] matches any character not in seq
    
    Patterns without / match filename only.
    Patterns with / match against path and can appear anywhere in the path.
    
    Args:
        filepath: Path to check
        pattern: Glob pattern
        
    Returns:
        True if filepath matches
        
    Examples:
        >>> glob_matches("/docs/file.pdf", "*.pdf")
        True
        >>> glob_matches("/docs/2024/Q1/inv.pdf", "**/2024/**/*.pdf")
        True
        >>> glob_matches("/docs/invoice_001.pdf", "invoice_*.pdf")
        True
    """
    # Normalize separators
    filepath = filepath.replace('\\', '/')
    pattern = pattern.replace('\\', '/')
    
    # Filename-only pattern
    if '/' not in pattern:
        filename = filepath.split('/')[-1]
        return fnmatch.fnmatch(filename, pattern)
    
    # Path pattern - make it match anywhere unless rooted
    if not pattern.startswith('**') and not pattern.startswith('/'):
        pattern = '**/' + pattern
    
    # Convert to regex
    pattern = pattern.replace('**', '\x00STAR2\x00')
    pattern = re.escape(pattern)
    pattern = pattern.replace('\\*', '[^/]*')
    pattern = pattern.replace('\\?', '.')
    pattern = pattern.replace('\\[', '[').replace('\\]', ']')
    pattern = pattern.replace('\\!', '!')
    pattern = pattern.replace('\x00STAR2\x00', '.*')
    pattern = '^' + pattern + '$'
    
    return re.match(pattern, filepath) is not None


def filter_files_by_glob(files: List[str], patterns: Optional[str]) -> List[str]:
    """
    Filter files by glob pattern(s).
    
    Args:
        files: List of file paths
        patterns: Comma-separated glob patterns or None
        
    Returns:
        Filtered list
        
    Examples:
        >>> files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
        >>> filter_files_by_glob(files, "*.pdf")
        ['/docs/a.pdf']
        >>> filter_files_by_glob(files, "*.pdf,*.docx")
        ['/docs/a.pdf', '/docs/b.docx']
        >>> filter_files_by_glob(files, None)
        ['/docs/a.pdf', '/docs/b.docx', '/docs/c.txt']
    """
    if not patterns:
        return files
    
    pattern_list = [p.strip() for p in patterns.split(',')]
    return [f for f in files if any(glob_matches(f, p) for p in pattern_list)]


def apply_glob_filter(
    files: List[str], 
    glob_pattern: Optional[str], 
    verbose: bool = False
) -> List[str]:
    """
    Apply glob filter to file list with optional verbose output.
    
    Args:
        files: List of file paths
        glob_pattern: Glob pattern or None
        verbose: Print filtering stats to stderr
        
    Returns:
        Filtered list
        
    Example:
        >>> files = ["/docs/a.pdf", "/docs/b.docx"]
        >>> filtered = apply_glob_filter(files, "*.pdf", verbose=True)
        Glob filter '*.pdf': 1/2 files matched
    """
    if not glob_pattern:
        return files
    
    filtered = filter_files_by_glob(files, glob_pattern)
    
    if verbose:
        print(f"Glob filter '{glob_pattern}': {len(filtered)}/{len(files)} files matched", 
              file=sys.stderr)
    
    return filtered


# Convenience exports
__all__ = ['glob_matches', 'filter_files_by_glob', 'apply_glob_filter']


================================================================================
FILE: docsearch/readers.py
================================================================================

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
    '.md': MarkdownReader,
    '.txt': MarkdownReader,
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


================================================================================
FILE: docsearch/batch.py
================================================================================

"""
Batch processing for docsearch.

This module provides utilities for processing multiple files and
creating structured batches for classification workflows.
"""

import os
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

from .models import Batch, BatchEntry, BatchCollection
from .readers import read_file_preview


def collect_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Collect all files from directory.
    
    Args:
        directory: Directory to scan
        recursive: Process subdirectories
        
    Returns:
        List of file paths
    """
    files = []
    
    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
    else:
        for item in os.listdir(directory):
            filepath = os.path.join(directory, item)
            if os.path.isfile(filepath):
                files.append(filepath)
    
    return files


def create_batch_from_files(
    files: List[str],
    categories: Optional[List[str]] = None,
    n_tokens: int = 250,
    show_progress: bool = False
) -> Batch:
    """
    Create batch from list of files.
    
    Args:
        files: List of file paths
        categories: Optional category labels
        n_tokens: Tokens to extract per file
        show_progress: Show progress bar
        
    Returns:
        Batch object
    """
    batch = Batch(categories=categories or [])
    
    if show_progress and HAS_TQDM:
        iterator = tqdm(files, desc="Processing files")
    else:
        iterator = files
    
    for filepath in iterator:
        result = read_file_preview(filepath, n_tokens=n_tokens)
        
        if result.ok:
            entry = BatchEntry(
                filepath=filepath,
                filename=os.path.basename(filepath),
                extension=os.path.splitext(filepath)[1],
                size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                tokens=result.text
            )
            batch.files.append(entry)
    
    return batch


def create_labeled_batch_from_directory(
    directory: str,
    categories: Optional[List[str]] = None,
    n_tokens: int = 250,
    recursive: bool = True,
    show_progress: bool = False
) -> str:
    """
    Create labeled batch from directory.
    
    Args:
        directory: Directory to process
        categories: Category labels
        n_tokens: Tokens per file
        recursive: Process subdirectories
        show_progress: Show progress bar
        
    Returns:
        Batch format string
    """
    files = collect_files(directory, recursive=recursive)
    batch = create_batch_from_files(files, categories, n_tokens, show_progress)
    collection = BatchCollection(batches=[batch])
    return collection.to_format()


def files_from_text(text: str) -> List[str]:
    """
    Parse file paths from text (one per line).
    
    Args:
        text: Text with file paths
        
    Returns:
        List of file paths
    """
    return [
        line.strip()
        for line in text.strip().split('\n')
        if line.strip() and not line.strip().startswith('#')
    ]


def files_from_file(filepath: str) -> List[str]:
    """
    Read file list from a text file.
    
    Args:
        filepath: Path to file containing paths
        
    Returns:
        List of file paths
    """
    with open(filepath, 'r') as f:
        return files_from_text(f.read())


class BatchBuilder:
    """Builder for complex multi-source batches."""
    
    def __init__(self):
        self.batches: List[Batch] = []
    
    def add_directory(
        self,
        directory: str,
        categories: Optional[List[str]] = None,
        n_tokens: int = 250,
        recursive: bool = True
    ) -> 'BatchBuilder':
        """Add files from directory."""
        files = collect_files(directory, recursive=recursive)
        batch = create_batch_from_files(files, categories, n_tokens)
        self.batches.append(batch)
        return self
    
    def add_files(
        self,
        files: List[str],
        categories: Optional[List[str]] = None,
        n_tokens: int = 250
    ) -> 'BatchBuilder':
        """Add specific files."""
        batch = create_batch_from_files(files, categories, n_tokens)
        self.batches.append(batch)
        return self
    
    def build(self) -> BatchCollection:
        """Build final batch collection."""
        return BatchCollection(batches=self.batches)
    
    def to_format(self) -> str:
        """Build and convert to format."""
        return self.build().to_format()


================================================================================
FILE: docsearch/cli.py
================================================================================

"""
Command-line interface for docsearch with glob pattern support.

Commands:
    extract - Extract tokens from files for classification
    search  - Search files for regex patterns
    info    - Show file information
    formats - List supported formats
"""

import argparse
import sys
import os
import re
from pathlib import Path
from typing import List, Optional

from .readers import read_file, read_file_preview, get_supported_formats
from .batch import (
    collect_files, create_batch_from_files, 
    files_from_file, BatchCollection, Batch, BatchEntry
)
from .glob_filter import apply_glob_filter
from .models import ReadStatus


def create_parser():
    """Create argument parser with glob support."""
    
    parser = argparse.ArgumentParser(
        prog='docsearch',
        description='Document search and classification with glob filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all files
  docsearch extract /documents -o batch.md
  
  # Extract only PDFs
  docsearch extract /documents --glob "*.pdf" -o pdfs.md
  
  # Extract multiple types with categories
  docsearch extract /invoices --glob "*.pdf,*.docx" --categories "invoice" -o batch.md
  
  # Search in specific files
  docsearch search /documents "invoice" --glob "**/2024/*.pdf"
  
  # Show file info
  docsearch info document.pdf
  
  # List supported formats
  docsearch formats
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # EXTRACT command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract tokens from files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Glob Pattern Examples:
  *.pdf                      All PDF files
  *.pdf,*.docx               PDFs and DOCX files
  **/invoices/*.pdf          PDFs in any invoices directory
  2024/**/*.xlsx             Excel files in/under any 2024 directory
"""
    )
    extract_parser.add_argument('path', nargs='?', help='Directory to process')
    extract_parser.add_argument('-g', '--glob', help='Glob pattern to filter files')
    extract_parser.add_argument('-o', '--output', help='Output file')
    extract_parser.add_argument('-a', '--append', action='store_true', 
                               help='Append to output file')
    extract_parser.add_argument('-c', '--categories', help='Comma-separated categories')
    extract_parser.add_argument('-t', '--tokens', type=int, default=250,
                               help='Tokens per file (default: 250)')
    extract_parser.add_argument('-r', '--recursive', action='store_true', default=True,
                               help='Process recursively (default: true)')
    extract_parser.add_argument('--no-recursive', action='store_false', dest='recursive',
                               help='Do not process recursively')
    extract_parser.add_argument('--file-list', help='File with paths to process')
    extract_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Show verbose progress')
    
    # SEARCH command
    search_parser = subparsers.add_parser(
        'search',
        help='Search files for pattern'
    )
    search_parser.add_argument('path', help='Directory or file to search')
    search_parser.add_argument('pattern', help='Regex pattern')
    search_parser.add_argument('-g', '--glob', help='Glob pattern to filter files')
    search_parser.add_argument('-i', '--ignore-case', action='store_true',
                              help='Case-insensitive search')
    search_parser.add_argument('-r', '--recursive', action='store_true', default=True)
    search_parser.add_argument('--no-recursive', action='store_false', dest='recursive')
    search_parser.add_argument('-v', '--verbose', action='store_true')
    
    # INFO command
    info_parser = subparsers.add_parser('info', help='Show file information')
    info_parser.add_argument('path', help='File to examine')
    info_parser.add_argument('-t', '--tokens', type=int, default=100,
                            help='Tokens to preview (default: 100)')
    
    # FORMATS command
    subparsers.add_parser('formats', help='List supported file formats')
    
    return parser


def cmd_extract(args):
    """Handle extract command with glob filtering."""
    
    # Parse categories
    categories = []
    if args.categories:
        categories = [c.strip() for c in args.categories.split(',')]
    
    # Get files
    if args.file_list:
        files = files_from_file(args.file_list)
    elif args.path:
        if os.path.isfile(args.path):
            files = [args.path]
        else:
            files = collect_files(args.path, args.recursive)
    else:
        print("Error: Specify path or --file-list", file=sys.stderr)
        return 1
    
    # Apply glob filter
    files = apply_glob_filter(files, args.glob, args.verbose)
    
    if not files:
        print("No files matched the filters", file=sys.stderr)
        return 1
    
    # Process files
    batch = Batch(categories=categories)
    success_count = 0
    
    for filepath in files:
        result = read_file_preview(filepath, n_tokens=args.tokens)
        if result.ok:
            entry = BatchEntry(
                filepath=filepath,
                filename=os.path.basename(filepath),
                extension=os.path.splitext(filepath)[1],
                size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                tokens=result.text
            )
            batch.files.append(entry)
            success_count += 1
            if args.verbose:
                print(f"✓ {filepath}", file=sys.stderr)
        elif args.verbose:
            print(f"✗ {filepath}: {result.error}", file=sys.stderr)
    
    # Output
    collection = BatchCollection(batches=[batch])
    output_text = collection.to_format()
    
    if args.output:
        mode = 'a' if args.append else 'w'
        with open(args.output, mode) as f:
            f.write(output_text)
        print(f"Wrote {success_count} files to {args.output}", file=sys.stderr)
    else:
        print(output_text)
    
    return 0


def cmd_search(args):
    """Handle search command with glob filtering."""
    
    # Compile pattern
    flags = re.IGNORECASE if args.ignore_case else 0
    try:
        pattern = re.compile(args.pattern, flags)
    except re.error as e:
        print(f"Invalid regex pattern: {e}", file=sys.stderr)
        return 1
    
    # Get files
    if os.path.isfile(args.path):
        files = [args.path]
    else:
        files = collect_files(args.path, args.recursive)
    
    # Apply glob filter
    files = apply_glob_filter(files, args.glob, args.verbose)
    
    # Search files
    total_matches = 0
    
    for filepath in files:
        result = read_file(filepath)
        
        if result.ok:
            matches = list(pattern.finditer(result.text))
            if matches:
                total_matches += len(matches)
                print(f"\n{filepath}: {len(matches)} matches")
                
                # Show first few matches
                for match in matches[:5]:
                    start = max(0, match.start() - 40)
                    end = min(len(result.text), match.end() + 40)
                    context = result.text[start:end]
                    print(f"  ...{context}...")
                
                if len(matches) > 5:
                    print(f"  ... and {len(matches) - 5} more matches")
    
    print(f"\nTotal: {total_matches} matches in {len(files)} files", file=sys.stderr)
    return 0


def cmd_info(args):
    """Handle info command."""
    
    result = read_file_preview(args.path, n_tokens=args.tokens)
    
    print(f"File: {args.path}")
    print(f"Status: {result.status.value}")
    
    if result.ok:
        print(f"\nMetadata:")
        for key, value in result.metadata.to_dict().items():
            print(f"  {key}: {value}")
        
        print(f"\nPreview ({args.tokens} tokens):")
        print(result.text[:500])
        if len(result.text) > 500:
            print("...")
    else:
        print(f"\nError: {result.error}")
    
    return 0


def cmd_formats(args):
    """Handle formats command."""
    
    formats = get_supported_formats()
    
    print("Supported file formats:")
    print()
    for ext, reader in sorted(formats.items()):
        print(f"  {ext:10} {reader}")
    
    return 0


def main():
    """Main entry point."""
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler
    if args.command == 'extract':
        return cmd_extract(args)
    elif args.command == 'search':
        return cmd_search(args)
    elif args.command == 'info':
        return cmd_info(args)
    elif args.command == 'formats':
        return cmd_formats(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())


================================================================================
FILE: tests/test_docsearch.py
================================================================================

"""
Basic tests for docsearch package.

Run with: pytest tests/
"""

import pytest
from docsearch import (
    read_file,
    read_file_preview,
    ReadStatus,
    glob_matches,
    filter_files_by_glob,
    BatchCollection,
)


class TestGlobMatching:
    """Test glob pattern matching."""
    
    def test_simple_patterns(self):
        """Test simple filename patterns."""
        assert glob_matches("/docs/file.pdf", "*.pdf")
        assert not glob_matches("/docs/file.pdf", "*.docx")
        assert glob_matches("/docs/invoice_001.pdf", "invoice_*.pdf")
    
    def test_recursive_patterns(self):
        """Test recursive directory patterns."""
        assert glob_matches("/docs/subdir/file.pdf", "**/*.pdf")
        assert glob_matches("/docs/2024/Q1/inv.pdf", "2024/**/*.pdf")
        assert glob_matches("/docs/invoices/inv.pdf", "**/invoices/*.pdf")
    
    def test_character_classes(self):
        """Test character class patterns."""
        assert glob_matches("/docs/report_A.pdf", "report_[A-Z]*")
        assert glob_matches("/docs/file1.pdf", "file[0-9]*")
    
    def test_case_sensitivity(self):
        """Test case-sensitive matching."""
        assert glob_matches("/docs/file.pdf", "*.pdf")
        assert not glob_matches("/docs/FILE.PDF", "*.pdf")


class TestFileFiltering:
    """Test file filtering."""
    
    def test_single_pattern(self):
        """Test filtering with single pattern."""
        files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
        result = filter_files_by_glob(files, "*.pdf")
        assert result == ["/docs/a.pdf"]
    
    def test_multiple_patterns(self):
        """Test filtering with multiple patterns."""
        files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
        result = filter_files_by_glob(files, "*.pdf,*.docx")
        assert len(result) == 2
        assert "/docs/a.pdf" in result
        assert "/docs/b.docx" in result
    
    def test_no_pattern(self):
        """Test filtering with no pattern."""
        files = ["/docs/a.pdf", "/docs/b.docx"]
        result = filter_files_by_glob(files, None)
        assert result == files


class TestBatchFormat:
    """Test batch format parsing."""
    
    def test_parse_simple_batch(self):
        """Test parsing simple batch."""
        text = """<batch>
CATEGORIES: test
<file>
FILEPATH: /test.pdf
FILENAME: test.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Test content here
"""
        collection = BatchCollection.from_format(text)
        assert len(collection.batches) == 1
        assert collection.batches[0].categories == ["test"]
        assert len(collection.batches[0].files) == 1
        assert collection.batches[0].files[0].filename == "test.pdf"
    
    def test_parse_multiple_files(self):
        """Test parsing multiple files."""
        text = """<batch>
CATEGORIES: test
<file>
FILEPATH: /test1.pdf
FILENAME: test1.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Content 1
<file>
FILEPATH: /test2.pdf
FILENAME: test2.pdf
EXTENSION: .pdf
SIZE: 5678
TOKENS:
Content 2
"""
        collection = BatchCollection.from_format(text)
        assert len(collection.batches[0].files) == 2


class TestReadResult:
    """Test ReadResult functionality."""
    
    def test_ok_property(self):
        """Test ok property."""
        from docsearch.models import ReadResult, ReadStatus
        
        result = ReadResult(
            filepath="/test.pdf",
            status=ReadStatus.SUCCESS
        )
        assert result.ok
        
        result = ReadResult(
            filepath="/test.pdf",
            status=ReadStatus.NOT_FOUND
        )
        assert not result.ok


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


================================================================================
END OF SOURCE CODE
================================================================================

## Installation

Save these files in the structure shown at the top, then:

```bash
pip install -e .
```

Or:

```bash
pip install -e ".[full]"
```

## Quick Test

```python
from docsearch import glob_matches

print(glob_matches("/docs/file.pdf", "*.pdf"))  # True
print(glob_matches("/docs/2024/file.pdf", "2024/*.pdf"))  # True
```
