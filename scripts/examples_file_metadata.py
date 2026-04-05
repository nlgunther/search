#!/usr/bin/env python3
"""
File Metadata Search Examples - DocSearch v2.2.0

Demonstrates searching and filtering files by file system metadata (dates, size)
and document metadata (PDF author, title, keywords).
"""

from docsearch import (
    FileMetadataFilter,
    search_by_metadata,
    filter_by_date,
    filter_by_size,
    filter_by_pdf_metadata,
    get_file_info,
    collect_files
)
from datetime import datetime, timedelta


def example_1_filter_by_date():
    """Example 1: Filter files by modification date."""
    print("=" * 60)
    print("Example 1: Filter by Modification Date")
    print("=" * 60)
    
    # Simulate file collection
    files = [
        '/docs/report_2024-01-15.pdf',
        '/docs/invoice_2024-03-20.pdf',
        '/docs/old_notes_2023-12-01.txt'
    ]
    
    print("\nFind files modified in 2024:")
    print("```python")
    print("from docsearch import filter_by_date")
    print()
    print("matches = filter_by_date(")
    print("    files,")
    print("    modified_after='2024-01-01',")
    print("    modified_before='2024-12-31'")
    print(")")
    print("```")
    
    print("\nThis would return files modified between Jan 1 and Dec 31, 2024")


def example_2_filter_by_size():
    """Example 2: Filter files by size."""
    print("\n" + "=" * 60)
    print("Example 2: Filter by File Size")
    print("=" * 60)
    
    print("\nFind large files (> 1 MB):")
    print("```python")
    print("from docsearch import filter_by_size")
    print()
    print("# Files larger than 1 MB")
    print("large_files = filter_by_size(files, min_bytes=1_000_000)")
    print()
    print("# Files between 100 KB and 10 MB")
    print("medium_files = filter_by_size(")
    print("    files,")
    print("    min_bytes=100_000,")
    print("    max_bytes=10_000_000")
    print(")")
    print("```")


def example_3_pdf_metadata():
    """Example 3: Search PDF metadata."""
    print("\n" + "=" * 60)
    print("Example 3: Search PDF Metadata")
    print("=" * 60)
    
    print("\nFind PDFs by author:")
    print("```python")
    print("from docsearch import filter_by_pdf_metadata")
    print()
    print("# Find all PDFs authored by John Doe")
    print("johns_docs = filter_by_pdf_metadata(")
    print("    files,")
    print("    author='John Doe'")
    print(")")
    print()
    print("# Find PDFs with 'invoice' in title (case-insensitive)")
    print("invoices = filter_by_pdf_metadata(")
    print("    files,")
    print("    title='invoice',")
    print("    case_sensitive=False")
    print(")")
    print("```")
    
    print("\nNote: Requires 'pypdf' package to be installed")


def example_4_combined_filters():
    """Example 4: Combine multiple filters."""
    print("\n" + "=" * 60)
    print("Example 4: Combined Filters")
    print("=" * 60)
    
    print("\nFind large PDFs modified recently:")
    print("```python")
    print("from docsearch import FileMetadataFilter, search_by_metadata")
    print("from datetime import datetime, timedelta")
    print()
    print("# Define criteria")
    print("week_ago = datetime.now() - timedelta(days=7)")
    print()
    print("criteria = FileMetadataFilter(")
    print("    extensions=['.pdf'],")
    print("    modified_after=week_ago,")
    print("    size_min=1_000_000  # 1 MB")
    print(")")
    print()
    print("# Search")
    print("matches = search_by_metadata(files, criteria)")
    print("```")


def example_5_real_world_workflow():
    """Example 5: Real-world workflow."""
    print("\n" + "=" * 60)
    print("Example 5: Real-World Workflow")
    print("=" * 60)
    
    print("\nWorkflow: Find recent invoices for review")
    print("```python")
    print("from docsearch import (")
    print("    collect_files,")
    print("    FileMetadataFilter,")
    print("    search_by_metadata")
    print(")")
    print("from datetime import datetime")
    print()
    print("# Step 1: Collect all files")
    print("all_files = collect_files('/accounting')")
    print()
    print("# Step 2: Define criteria")
    print("criteria = FileMetadataFilter(")
    print("    # Filename contains 'invoice'")
    print("    name_pattern='invoice',")
    print("    name_case_sensitive=False,")
    print("    # Only PDFs")
    print("    extensions=['.pdf'],")
    print("    # Modified in January 2024")
    print("    modified_after='2024-01-01',")
    print("    modified_before='2024-01-31',")
    print("    # At least 50 KB")
    print("    size_min=50_000")
    print(")")
    print()
    print("# Step 3: Search")
    print("invoices = search_by_metadata(all_files, criteria)")
    print()
    print("# Step 4: Review")
    print("for invoice in invoices:")
    print("    print(f'Review: {invoice}')")
    print("```")


def example_6_get_file_info():
    """Example 6: Get detailed file information."""
    print("\n" + "=" * 60)
    print("Example 6: Get Detailed File Information")
    print("=" * 60)
    
    print("\nGet comprehensive file metadata:")
    print("```python")
    print("from docsearch import get_file_info")
    print()
    print("info = get_file_info('/docs/report.pdf')")
    print()
    print("print(f\"File: {info['filename']}\")")
    print("print(f\"Size: {info['size']:,} bytes\")")
    print("print(f\"Modified: {info['modified']}\")")
    print("print(f\"Created: {info['created']}\")")
    print()
    print("if info['pdf_metadata']:")
    print("    print(f\"Author: {info['pdf_metadata']['author']}\")")
    print("    print(f\"Title: {info['pdf_metadata']['title']}\")")
    print("```")


def example_7_date_formats():
    """Example 7: Different date input formats."""
    print("\n" + "=" * 60)
    print("Example 7: Date Input Formats")
    print("=" * 60)
    
    print("\nMultiple ways to specify dates:")
    print("```python")
    print("from docsearch import filter_by_date")
    print("from datetime import datetime, date, timedelta")
    print()
    print("# Method 1: ISO string (YYYY-MM-DD)")
    print("matches = filter_by_date(files, modified_after='2024-01-01')")
    print()
    print("# Method 2: datetime object")
    print("week_ago = datetime.now() - timedelta(days=7)")
    print("matches = filter_by_date(files, modified_after=week_ago)")
    print()
    print("# Method 3: date object")
    print("today = date.today()")
    print("matches = filter_by_date(files, modified_before=today)")
    print()
    print("# Method 4: ISO with time")
    print("matches = filter_by_date(files, modified_after='2024-01-01 09:00:00')")
    print("```")


def example_8_comparison():
    """Example 8: Comparison with other search methods."""
    print("\n" + "=" * 60)
    print("Example 8: Comparison of Search Methods")
    print("=" * 60)
    
    print("\nDocSearch v2.2.0 has three search modes:")
    print()
    print("1. **Filename Search** (v2.1.0 - fastest)")
    print("   - Searches only filenames/paths")
    print("   - No file reading")
    print("   - Use: search_metadata()")
    print()
    print("2. **File Metadata Search** (v2.2.0 - NEW)")
    print("   - Searches dates, sizes, PDF metadata")
    print("   - Minimal file reading (only stats + PDF metadata if needed)")
    print("   - Use: filter_by_date(), filter_by_size(), etc.")
    print()
    print("3. **Content Search** (v2.0.0 - slowest but thorough)")
    print("   - Searches inside file contents")
    print("   - Reads entire files")
    print("   - Use: docsearch search (CLI) or read_file() (Python)")
    print()
    print("**Choose the right tool:**")
    print("- Finding files by name pattern → search_metadata()")
    print("- Finding files by date/size → filter_by_date()/filter_by_size()")
    print("- Finding text in documents → content search")


def main():
    """Run all examples."""
    print("DocSearch v2.2.0 - File Metadata Search Examples")
    print()
    
    example_1_filter_by_date()
    example_2_filter_by_size()
    example_3_pdf_metadata()
    example_4_combined_filters()
    example_5_real_world_workflow()
    example_6_get_file_info()
    example_7_date_formats()
    example_8_comparison()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("For more information, see:")
    print("- API.md for complete API reference")
    print("- CHEATSHEET.md for quick examples")


if __name__ == "__main__":
    main()
