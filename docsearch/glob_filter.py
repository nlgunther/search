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
    
    On Windows: Case-insensitive matching (*.csv matches *.CSV)
    On Unix/Linux: Case-sensitive matching (*.csv does NOT match *.CSV)
    
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
        >>> # On Windows: case-insensitive
        >>> glob_matches("/docs/file.PDF", "*.pdf")  # Windows: True, Linux: False
        >>> glob_matches("/docs/2024/Q1/inv.pdf", "**/2024/**/*.pdf")
        True
    """
    import platform
    
    # Normalize separators
    filepath = filepath.replace('\\', '/')
    pattern = pattern.replace('\\', '/')
    
    # Use case-insensitive matching on Windows
    # Windows filesystem is case-insensitive, so *.csv should match *.CSV
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        filepath_compare = filepath.lower()
        pattern_compare = pattern.lower()
    else:
        filepath_compare = filepath
        pattern_compare = pattern
    
    # Filename-only pattern
    if '/' not in pattern_compare:
        filename = filepath_compare.split('/')[-1]
        # Use fnmatch (case-insensitive on Windows, case-sensitive on Unix)
        if is_windows:
            return fnmatch.fnmatch(filename, pattern_compare)
        else:
            return fnmatch.fnmatchcase(filename, pattern_compare)
    
    # Path pattern - make it match anywhere unless rooted
    if not pattern_compare.startswith('**') and not pattern_compare.startswith('/'):
        pattern_compare = '**/' + pattern_compare
    
    # Convert to regex
    pattern_regex = pattern_compare.replace('**', '\x00STAR2\x00')
    pattern_regex = re.escape(pattern_regex)
    pattern_regex = pattern_regex.replace('\\*', '[^/]*')
    pattern_regex = pattern_regex.replace('\\?', '.')
    pattern_regex = pattern_regex.replace('\\[', '[').replace('\\]', ']')
    pattern_regex = pattern_regex.replace('\\!', '!')
    pattern_regex = pattern_regex.replace('\x00STAR2\x00', '.*')
    pattern_regex = '^' + pattern_regex + '$'
    
    # Match (case-insensitive on Windows)
    if is_windows:
        return re.match(pattern_regex, filepath_compare, re.IGNORECASE) is not None
    else:
        return re.match(pattern_regex, filepath_compare) is not None


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
