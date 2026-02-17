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
