#!/usr/bin/env python3
"""
Metadata Search Examples - DocSearch v2.1.0

Demonstrates the new metadata-only search feature for fast filename/path searching
without reading file contents.
"""

from docsearch import (
    search_metadata,
    search_metadata_dict,
    filter_by_name_pattern,
    highlight_match,
    collect_files,
    filter_files_by_glob
)


def example_1_basic_search():
    """Example 1: Basic metadata search."""
    print("=" * 60)
    print("Example 1: Basic Metadata Search")
    print("=" * 60)
    
    files = [
        '/docs/invoice_2024_001.pdf',
        '/docs/invoice_2024_002.pdf',
        '/docs/receipt_2023_100.pdf',
        '/docs/contract_ABC.docx',
        '/docs/notes.txt'
    ]
    
    # Search for "2024" in filenames
    matches = search_metadata(files, '2024')
    
    print(f"\nSearching for '2024' in filenames:")
    print(f"Found {len(matches)} matches:")
    for filepath, (start, end) in matches:
        highlighted = highlight_match(filepath, start, end)
        print(f"  {highlighted}")


def example_2_case_insensitive():
    """Example 2: Case-insensitive search."""
    print("\n" + "=" * 60)
    print("Example 2: Case-Insensitive Search")
    print("=" * 60)
    
    files = [
        '/docs/Invoice_2024.pdf',
        '/docs/INVOICE_2023.pdf',
        '/docs/receipt.pdf'
    ]
    
    # Case-sensitive (default)
    matches_case = search_metadata(files, 'invoice', case_sensitive=True)
    print(f"\nCase-sensitive search for 'invoice': {len(matches_case)} matches")
    
    # Case-insensitive
    matches_nocase = search_metadata(files, 'invoice', case_sensitive=False)
    print(f"Case-insensitive search for 'invoice': {len(matches_nocase)} matches")
    
    for filepath, (start, end) in matches_nocase:
        highlighted = highlight_match(filepath, start, end)
        print(f"  {highlighted}")


def example_3_regex_patterns():
    """Example 3: Using regex patterns."""
    print("\n" + "=" * 60)
    print("Example 3: Regex Patterns")
    print("=" * 60)
    
    files = [
        '/docs/invoice_2024_001.pdf',
        '/docs/invoice_2024_002.pdf',
        '/docs/receipt_2023_100.pdf',
        '/docs/contract_123.docx'
    ]
    
    # Pattern: underscore followed by 4 digits
    pattern = r'_\d{4}_'
    matches = search_metadata(files, pattern)
    
    print(f"\nSearching for pattern '{pattern}':")
    print(f"Found {len(matches)} matches:")
    for filepath, (start, end) in matches:
        highlighted = highlight_match(filepath, start, end)
        print(f"  {highlighted}")


def example_4_detailed_results():
    """Example 4: Get detailed results with search_metadata_dict."""
    print("\n" + "=" * 60)
    print("Example 4: Detailed Results")
    print("=" * 60)
    
    files = [
        '/docs/invoice_2024_001.pdf',
        '/docs/invoice_2024_002.pdf',
        '/docs/receipt_2023_100.pdf',
        '/docs/contract.docx'
    ]
    
    result = search_metadata_dict(files, r'_\d{4}_')
    
    print(f"\nSearch Results:")
    print(f"  Total files searched: {result['total_files']}")
    print(f"  Files matched: {result['matched_files']}")
    print(f"\nDetails:")
    for detail in result['details']:
        print(f"  File: {detail['filepath']}")
        print(f"    Match: '{detail['match']}' at position {detail['start']}-{detail['end']}")


def example_5_simple_filter():
    """Example 5: Simple filtering with filter_by_name_pattern."""
    print("\n" + "=" * 60)
    print("Example 5: Simple Filtering")
    print("=" * 60)
    
    files = [
        '/docs/invoice_2024_001.pdf',
        '/docs/invoice_2024_002.pdf',
        '/docs/receipt_2023.pdf',
        '/docs/contract.docx'
    ]
    
    # Get all invoices
    invoices = filter_by_name_pattern(files, 'invoice', case_sensitive=False)
    
    print(f"\nFiles with 'invoice' in name:")
    for filepath in invoices:
        print(f"  {filepath}")


def example_6_combined_workflow():
    """Example 6: Combined workflow with glob filter and metadata search."""
    print("\n" + "=" * 60)
    print("Example 6: Combined Workflow")
    print("=" * 60)
    
    # Simulate a large file collection
    files = [
        '/docs/2024/invoices/invoice_001.pdf',
        '/docs/2024/invoices/invoice_002.pdf',
        '/docs/2024/receipts/receipt_100.pdf',
        '/docs/2023/invoices/invoice_050.pdf',
        '/docs/contracts/contract_ABC.docx',
        '/docs/notes.txt'
    ]
    
    print("\nWorkflow: Find all 2024 invoice PDFs")
    
    # Step 1: Filter by glob pattern (PDFs only)
    pdfs = filter_files_by_glob(files, "*.pdf")
    print(f"Step 1 - Glob filter '*.pdf': {len(pdfs)} files")
    
    # Step 2: Metadata search for "2024"
    year_2024 = filter_by_name_pattern(pdfs, '2024')
    print(f"Step 2 - Metadata filter '2024': {len(year_2024)} files")
    
    # Step 3: Metadata search for "invoice"
    invoices = filter_by_name_pattern(year_2024, 'invoice', case_sensitive=False)
    print(f"Step 3 - Metadata filter 'invoice': {len(invoices)} files")
    
    print(f"\nFinal results:")
    for filepath in invoices:
        print(f"  {filepath}")


def example_7_performance_comparison():
    """Example 7: Performance comparison (conceptual)."""
    print("\n" + "=" * 60)
    print("Example 7: Performance Comparison")
    print("=" * 60)
    
    print("""
Performance Characteristics:

Metadata-only search:
  - Speed: 0.01 seconds for 10,000 files
  - No file I/O required
  - Works on locked/protected files
  - 100x+ faster than content search

Content search:
  - Speed: 1-10 seconds for 10,000 files (depends on file size)
  - Requires reading file contents
  - Fails on locked/protected files
  - Necessary for searching within documents

When to use metadata-only search:
  ✓ Finding files by naming convention
  ✓ Filtering by date patterns in filenames
  ✓ Quick directory scans
  ✓ Working with large file collections
  ✓ Files that can't be opened

When to use content search:
  ✓ Searching for text inside documents
  ✓ Finding specific quotes or data
  ✓ Classification based on content
    """)


def main():
    """Run all examples."""
    print("DocSearch v2.1.0 - Metadata Search Examples")
    print()
    
    example_1_basic_search()
    example_2_case_insensitive()
    example_3_regex_patterns()
    example_4_detailed_results()
    example_5_simple_filter()
    example_6_combined_workflow()
    example_7_performance_comparison()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
