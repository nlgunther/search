"""
File metadata search for docsearch.

Search and filter files by file system metadata (dates, size) and 
document metadata (PDF author, title, etc.).
"""

import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class FileMetadataFilter:
    """Filter criteria for file metadata search."""
    
    # Filename/path filters
    name_pattern: Optional[str] = None
    name_case_sensitive: bool = True
    
    # Date filters (can be datetime, date, or ISO string)
    modified_after: Optional[Union[datetime, date, str]] = None
    modified_before: Optional[Union[datetime, date, str]] = None
    created_after: Optional[Union[datetime, date, str]] = None
    created_before: Optional[Union[datetime, date, str]] = None
    
    # Size filters (in bytes)
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    
    # Extension filter
    extensions: Optional[List[str]] = None
    
    # PDF metadata filters (requires file reading)
    pdf_author: Optional[str] = None
    pdf_title: Optional[str] = None
    pdf_keywords: Optional[str] = None
    pdf_case_sensitive: bool = False


def _parse_date(date_input: Union[datetime, date, str, None]) -> Optional[datetime]:
    """
    Parse date input to datetime object.
    
    Args:
        date_input: datetime, date, ISO string, or None
        
    Returns:
        datetime object or None
    """
    if date_input is None:
        return None
    
    if isinstance(date_input, datetime):
        return date_input
    
    if isinstance(date_input, date):
        return datetime.combine(date_input, datetime.min.time())
    
    if isinstance(date_input, str):
        # Try ISO format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
        try:
            return datetime.fromisoformat(date_input)
        except ValueError:
            # Try date only
            try:
                d = datetime.strptime(date_input, '%Y-%m-%d')
                return d
            except ValueError:
                raise ValueError(f"Invalid date format: {date_input}. Use ISO format (YYYY-MM-DD)")
    
    return None


def _get_file_stats(filepath: str) -> Dict[str, Any]:
    """
    Get file system metadata.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file stats
    """
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'exists': True
        }
    except (OSError, FileNotFoundError):
        return {
            'size': 0,
            'modified': None,
            'created': None,
            'exists': False
        }


def _get_pdf_metadata(filepath: str) -> Dict[str, Optional[str]]:
    """
    Extract PDF metadata (requires pypdf).
    
    Args:
        filepath: Path to PDF file
        
    Returns:
        Dictionary with PDF metadata
    """
    metadata = {
        'author': None,
        'title': None,
        'keywords': None,
        'subject': None,
        'creator': None,
        'producer': None
    }
    
    if not filepath.lower().endswith('.pdf'):
        return metadata
    
    try:
        import pypdf
        
        with open(filepath, 'rb') as f:
            reader = pypdf.PdfReader(f)
            info = reader.metadata
            
            if info:
                metadata['author'] = info.get('/Author', None)
                metadata['title'] = info.get('/Title', None)
                metadata['keywords'] = info.get('/Keywords', None)
                metadata['subject'] = info.get('/Subject', None)
                metadata['creator'] = info.get('/Creator', None)
                metadata['producer'] = info.get('/Producer', None)
    except (ImportError, Exception):
        # pypdf not available or file couldn't be read
        pass
    
    return metadata


def search_by_metadata(
    files: List[str],
    filter_criteria: FileMetadataFilter
) -> List[str]:
    """
    Search files by metadata criteria.
    
    Args:
        files: List of file paths to search
        filter_criteria: FileMetadataFilter with search criteria
        
    Returns:
        List of file paths matching all criteria
        
    Examples:
        >>> from docsearch import search_by_metadata, FileMetadataFilter
        >>> 
        >>> # Find large files modified in 2024
        >>> criteria = FileMetadataFilter(
        ...     modified_after='2024-01-01',
        ...     modified_before='2024-12-31',
        ...     size_min=1_000_000  # 1 MB
        ... )
        >>> matches = search_by_metadata(files, criteria)
        >>> 
        >>> # Find PDFs by author
        >>> criteria = FileMetadataFilter(
        ...     extensions=['.pdf'],
        ...     pdf_author='John Doe'
        ... )
        >>> matches = search_by_metadata(files, criteria)
    """
    # Parse date filters
    mod_after = _parse_date(filter_criteria.modified_after)
    mod_before = _parse_date(filter_criteria.modified_before)
    create_after = _parse_date(filter_criteria.created_after)
    create_before = _parse_date(filter_criteria.created_before)
    
    # Compile name pattern if provided
    name_pattern = None
    if filter_criteria.name_pattern:
        flags = 0 if filter_criteria.name_case_sensitive else re.IGNORECASE
        name_pattern = re.compile(filter_criteria.name_pattern, flags)
    
    matches = []
    
    for filepath in files:
        # Name pattern filter
        if name_pattern and not name_pattern.search(filepath):
            continue
        
        # Extension filter
        if filter_criteria.extensions:
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in [e.lower() for e in filter_criteria.extensions]:
                continue
        
        # Get file stats
        stats = _get_file_stats(filepath)
        if not stats['exists']:
            continue
        
        # Size filters
        if filter_criteria.size_min is not None and stats['size'] < filter_criteria.size_min:
            continue
        if filter_criteria.size_max is not None and stats['size'] > filter_criteria.size_max:
            continue
        
        # Date filters
        if mod_after and stats['modified'] < mod_after:
            continue
        if mod_before and stats['modified'] > mod_before:
            continue
        if create_after and stats['created'] < create_after:
            continue
        if create_before and stats['created'] > create_before:
            continue
        
        # PDF metadata filters (expensive - only if needed)
        if any([filter_criteria.pdf_author, filter_criteria.pdf_title, filter_criteria.pdf_keywords]):
            pdf_meta = _get_pdf_metadata(filepath)
            
            if filter_criteria.pdf_author:
                if not pdf_meta['author']:
                    continue
                pattern = filter_criteria.pdf_author
                flags = re.IGNORECASE if not filter_criteria.pdf_case_sensitive else 0
                if not re.search(pattern, pdf_meta['author'], flags):
                    continue
            
            if filter_criteria.pdf_title:
                if not pdf_meta['title']:
                    continue
                pattern = filter_criteria.pdf_title
                flags = re.IGNORECASE if not filter_criteria.pdf_case_sensitive else 0
                if not re.search(pattern, pdf_meta['title'], flags):
                    continue
            
            if filter_criteria.pdf_keywords:
                if not pdf_meta['keywords']:
                    continue
                pattern = filter_criteria.pdf_keywords
                flags = re.IGNORECASE if not filter_criteria.pdf_case_sensitive else 0
                if not re.search(pattern, pdf_meta['keywords'], flags):
                    continue
        
        # All filters passed
        matches.append(filepath)
    
    return matches


def filter_by_date(
    files: List[str],
    modified_after: Optional[Union[datetime, date, str]] = None,
    modified_before: Optional[Union[datetime, date, str]] = None,
    created_after: Optional[Union[datetime, date, str]] = None,
    created_before: Optional[Union[datetime, date, str]] = None
) -> List[str]:
    """
    Filter files by modification/creation dates (convenience function).
    
    Args:
        files: List of file paths
        modified_after: Only files modified after this date
        modified_before: Only files modified before this date
        created_after: Only files created after this date
        created_before: Only files created before this date
        
    Returns:
        List of matching file paths
        
    Examples:
        >>> # Files modified in January 2024
        >>> matches = filter_by_date(
        ...     files,
        ...     modified_after='2024-01-01',
        ...     modified_before='2024-01-31'
        ... )
        >>> 
        >>> # Files created in the last week
        >>> from datetime import datetime, timedelta
        >>> week_ago = datetime.now() - timedelta(days=7)
        >>> matches = filter_by_date(files, created_after=week_ago)
    """
    criteria = FileMetadataFilter(
        modified_after=modified_after,
        modified_before=modified_before,
        created_after=created_after,
        created_before=created_before
    )
    return search_by_metadata(files, criteria)


def filter_by_size(
    files: List[str],
    min_bytes: Optional[int] = None,
    max_bytes: Optional[int] = None
) -> List[str]:
    """
    Filter files by size (convenience function).
    
    Args:
        files: List of file paths
        min_bytes: Minimum file size in bytes
        max_bytes: Maximum file size in bytes
        
    Returns:
        List of matching file paths
        
    Examples:
        >>> # Files larger than 1 MB
        >>> large = filter_by_size(files, min_bytes=1_000_000)
        >>> 
        >>> # Files between 100 KB and 10 MB
        >>> medium = filter_by_size(files, min_bytes=100_000, max_bytes=10_000_000)
    """
    criteria = FileMetadataFilter(
        size_min=min_bytes,
        size_max=max_bytes
    )
    return search_by_metadata(files, criteria)


def filter_by_pdf_metadata(
    files: List[str],
    author: Optional[str] = None,
    title: Optional[str] = None,
    keywords: Optional[str] = None,
    case_sensitive: bool = False
) -> List[str]:
    """
    Filter PDF files by metadata (convenience function).
    
    Requires pypdf to be installed.
    
    Args:
        files: List of file paths
        author: Pattern to match in author field
        title: Pattern to match in title field
        keywords: Pattern to match in keywords field
        case_sensitive: Case-sensitive matching
        
    Returns:
        List of matching PDF file paths
        
    Examples:
        >>> # PDFs by specific author
        >>> docs = filter_by_pdf_metadata(files, author='John Doe')
        >>> 
        >>> # PDFs with "invoice" in title
        >>> invoices = filter_by_pdf_metadata(files, title='invoice', case_sensitive=False)
    """
    criteria = FileMetadataFilter(
        extensions=['.pdf'],
        pdf_author=author,
        pdf_title=title,
        pdf_keywords=keywords,
        pdf_case_sensitive=case_sensitive
    )
    return search_by_metadata(files, criteria)


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file information
        
    Example:
        >>> info = get_file_info('/docs/report.pdf')
        >>> print(f"Size: {info['size']} bytes")
        >>> print(f"Modified: {info['modified']}")
        >>> print(f"PDF Author: {info['pdf_metadata']['author']}")
    """
    stats = _get_file_stats(filepath)
    
    info = {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'extension': os.path.splitext(filepath)[1],
        'exists': stats['exists'],
        'size': stats['size'],
        'modified': stats['modified'],
        'created': stats['created'],
        'pdf_metadata': None
    }
    
    # Add PDF metadata if it's a PDF
    if filepath.lower().endswith('.pdf'):
        info['pdf_metadata'] = _get_pdf_metadata(filepath)
    
    return info
