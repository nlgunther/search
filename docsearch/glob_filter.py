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
    Check if filepath matches glob pattern (case-sensitive).
    
    Supports:
    - * matches any characters except /
    - ** matches any characters including /
    - ? matches single character
    - [seq] matches any character in seq
    - [!seq] matches any character not in seq
    
    Patterns without / match filename only.
    Patterns with / match against path and can appear anywhere in the path.
    
    Note: Matching is always case-sensitive regardless of platform.
    
    Args:
        filepath: Path to check
        pattern: Glob pattern (case-sensitive)
        
    Returns:
        True if filepath matches
        
    Examples:
        >>> glob_matches("/docs/file.pdf", "*.pdf")
        True
        >>> glob_matches("/docs/file.PDF", "*.pdf")
        False
        >>> glob_matches("/docs/2024/Q1/inv.pdf", "**/2024/**/*.pdf")
        True
    """
    # Normalize separators
    filepath = filepath.replace('\\', '/')
    pattern = pattern.replace('\\', '/')
    
    # Filename-only pattern
    if '/' not in pattern:
        filename = filepath.split('/')[-1]
        # Use fnmatchcase for case-sensitive matching on all platforms
        return fnmatch.fnmatchcase(filename, pattern)
    
    # Path pattern - make it match anywhere unless rooted
    if not pattern.startswith('**') and not pattern.startswith('/'):
        pattern = '**/' + pattern
    
    # Convert to regex (case-sensitive)
    pattern = pattern.replace('**', '\x00STAR2\x00')
    pattern = re.escape(pattern)
    pattern = pattern.replace('\\*', '[^/]*')
    pattern = pattern.replace('\\?', '.')
    pattern = pattern.replace('\\[', '[').replace('\\]', ']')
    pattern = pattern.replace('\\!', '!')
    pattern = pattern.replace('\x00STAR2\x00', '.*')
    pattern = '^' + pattern + '$'
    
    # Use case-sensitive regex matching
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
