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

__version__ = "2.0.1"

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
