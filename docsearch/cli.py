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
from .metadata_search import highlight_match
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
        help='Search files for pattern',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Search Modes:
  Default:          Search file contents
  --metadata-only:  Search filenames/paths only (fast, no file reading)

Examples:
  # Search file contents
  docsearch search /docs "invoice" --glob "*.pdf"
  
  # Search filenames only (fast)
  docsearch search /docs "2024-\d+" --metadata-only
  
  # Find files with "invoice" in path
  docsearch search /docs "invoice" --metadata-only -i
"""
    )
    search_parser.add_argument('path', help='Directory or file to search')
    search_parser.add_argument('pattern', help='Regex pattern')
    search_parser.add_argument('-g', '--glob', help='Glob pattern to filter files')
    search_parser.add_argument('-i', '--ignore-case', action='store_true',
                              help='Case-insensitive search')
    search_parser.add_argument('-m', '--metadata-only', action='store_true',
                              help='Search filenames/paths only (no file reading)')
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


def _search_metadata(files, pattern, verbose):
    """
    Search only filenames/paths (no file reading).
    
    Args:
        files: List of file paths
        pattern: Compiled regex pattern
        verbose: Show verbose output
        
    Returns:
        Exit code (0 = success)
    """
    matches_found = []
    
    for filepath in files:
        if verbose:
            print(f"Checking: {filepath}", file=sys.stderr)
        
        # Search in full path
        match = pattern.search(filepath)
        if match:
            matches_found.append((filepath, match.span()))
    
    # Display results
    if matches_found:
        print(f"\nMatched files:")
        for filepath, (start, end) in matches_found:
            # Highlight the match in the path
            highlighted = highlight_match(filepath, start, end)
            print(f"  {highlighted}")
    
    print(f"\nTotal: {len(matches_found)} files matched (out of {len(files)} searched)", file=sys.stderr)
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
    
    # Metadata-only search (fast - no file reading)
    if args.metadata_only:
        return _search_metadata(files, pattern, args.verbose)
    
    # Content search (reads files)
    total_matches = 0
    files_with_matches = 0
    
    for filepath in files:
        if args.verbose:
            print(f"Searching: {filepath}", file=sys.stderr)
        
        result = read_file(filepath)
        
        if result.ok:
            matches = list(pattern.finditer(result.text))
            if matches:
                files_with_matches += 1
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
    
    print(f"\nTotal: {total_matches} matches in {files_with_matches}/{len(files)} files", file=sys.stderr)
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
