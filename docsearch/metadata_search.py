"""
Metadata search functions for docsearch.

Search filenames and paths without reading file contents.
"""

import re
from typing import List, Pattern, Tuple, Union


def search_metadata(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> List[Tuple[str, Tuple[int, int]]]:
    r"""
    Search for pattern in filenames/paths only (no file reading).
    
    This is much faster than content search since it doesn't open files.
    Useful for finding files by name patterns.
    
    Args:
        files: List of file paths to search
        pattern: Regex pattern (string or compiled pattern)
        case_sensitive: Whether search is case-sensitive (default: True)
        
    Returns:
        List of tuples: (filepath, (match_start, match_end))
        
    Examples:
        >>> files = ['/docs/invoice_2024.pdf', '/docs/report.docx']
        >>> matches = search_metadata(files, '2024')
        >>> print(matches)
        [('/docs/invoice_2024.pdf', (13, 17))]
        
        >>> # Case-insensitive
        >>> matches = search_metadata(files, 'INVOICE', case_sensitive=False)
        >>> print(matches)
        [('/docs/invoice_2024.pdf', (6, 13))]
        
        >>> # Regex pattern
        >>> matches = search_metadata(files, r'_\d{4}')
        >>> print(matches)
        [('/docs/invoice_2024.pdf', (12, 17))]
    """
    # Compile pattern if string
    if isinstance(pattern, str):
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(pattern, flags)
    
    matches = []
    for filepath in files:
        match = pattern.search(filepath)
        if match:
            matches.append((filepath, match.span()))
    
    return matches


def search_metadata_dict(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> dict:
    """
    Search metadata and return results as a dictionary.
    
    Args:
        files: List of file paths to search
        pattern: Regex pattern (string or compiled pattern)
        case_sensitive: Whether search is case-sensitive (default: True)
        
    Returns:
        Dictionary with:
            - 'matches': List of matched file paths
            - 'total_files': Total number of files searched
            - 'matched_files': Number of files matched
            - 'details': List of dicts with filepath, match, start, end
            
    Example:
        >>> result = search_metadata_dict(['/docs/inv_2024.pdf'], '2024')
        >>> print(result['matched_files'])
        1
        >>> print(result['details'][0]['match'])
        '2024'
    """
    # Compile pattern if string
    if isinstance(pattern, str):
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(pattern, flags)
    
    matches = []
    details = []
    
    for filepath in files:
        match = pattern.search(filepath)
        if match:
            matches.append(filepath)
            details.append({
                'filepath': filepath,
                'match': match.group(),
                'start': match.start(),
                'end': match.end()
            })
    
    return {
        'matches': matches,
        'total_files': len(files),
        'matched_files': len(matches),
        'details': details
    }


def filter_by_name_pattern(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> List[str]:
    """
    Filter files by name pattern (convenience function).
    
    Returns only the list of matching file paths.
    
    Args:
        files: List of file paths to filter
        pattern: Regex pattern (string or compiled pattern)
        case_sensitive: Whether search is case-sensitive (default: True)
        
    Returns:
        List of file paths that match the pattern
        
    Example:
        >>> files = ['/docs/invoice_2024.pdf', '/docs/report.docx']
        >>> matched = filter_by_name_pattern(files, '2024')
        >>> print(matched)
        ['/docs/invoice_2024.pdf']
    """
    matches = search_metadata(files, pattern, case_sensitive)
    return [filepath for filepath, _ in matches]


def highlight_match(filepath: str, start: int, end: int, 
                   left_marker: str = '[', right_marker: str = ']') -> str:
    """
    Highlight matched portion in filepath.
    
    Args:
        filepath: Full file path
        start: Match start position
        end: Match end position
        left_marker: String to mark start of match (default: '[')
        right_marker: String to mark end of match (default: ']')
        
    Returns:
        String with match highlighted
        
    Example:
        >>> highlight_match('/docs/invoice_2024.pdf', 13, 17)
        '/docs/invoice_[2024].pdf'
    """
    before = filepath[:start]
    matched = filepath[start:end]
    after = filepath[end:]
    return f"{before}{left_marker}{matched}{right_marker}{after}"
