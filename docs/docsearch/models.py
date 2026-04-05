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
                    current_file['tokens'] = '\n'.join(tokens_lines)
                    entry = BatchEntry(**current_file)
                    current_batch.files.append(entry)
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
