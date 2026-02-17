#!/usr/bin/env python3
"""
Quick test to verify DocSearch v2.0.1 fixes.

Run this after installing the package to verify both bugs are fixed.
"""

def test_case_sensitivity():
    """Test case-sensitive glob matching."""
    from docsearch import glob_matches
    
    print("Testing case-sensitive glob matching...")
    
    tests = [
        ("/docs/file.pdf", "*.pdf", True, "lowercase pattern matches lowercase file"),
        ("/docs/file.PDF", "*.PDF", True, "uppercase pattern matches uppercase file"),
        ("/docs/file.pdf", "*.PDF", False, "uppercase pattern does NOT match lowercase file"),
        ("/docs/FILE.PDF", "*.pdf", False, "lowercase pattern does NOT match uppercase file"),
    ]
    
    all_passed = True
    for filepath, pattern, expected, description in tests:
        result = glob_matches(filepath, pattern)
        if result == expected:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ FAILED: {description}")
            print(f"    glob_matches('{filepath}', '{pattern}') = {result}, expected {expected}")
            all_passed = False
    
    return all_passed


def test_batch_parsing():
    """Test batch parsing with multiple files."""
    from docsearch.models import BatchCollection
    
    print("\nTesting batch parsing with multiple files...")
    
    batch_text = """<batch>
CATEGORIES: test
<file>
FILEPATH: /test1.pdf
FILENAME: test1.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Content of first file
<file>
FILEPATH: /test2.pdf
FILENAME: test2.pdf
EXTENSION: .pdf
SIZE: 5678
TOKENS:
Content of second file
"""
    
    try:
        collection = BatchCollection.from_format(batch_text)
        
        if len(collection.batches) != 1:
            print(f"  ✗ FAILED: Expected 1 batch, got {len(collection.batches)}")
            return False
        
        if len(collection.batches[0].files) != 2:
            print(f"  ✗ FAILED: Expected 2 files, got {len(collection.batches[0].files)}")
            return False
        
        if collection.batches[0].files[0].filename != "test1.pdf":
            print(f"  ✗ FAILED: First file should be test1.pdf")
            return False
        
        if collection.batches[0].files[1].filename != "test2.pdf":
            print(f"  ✗ FAILED: Second file should be test2.pdf")
            return False
        
        print("  ✓ Successfully parsed batch with 2 files")
        print("  ✓ Correct filenames extracted")
        return True
        
    except Exception as e:
        print(f"  ✗ FAILED with exception: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("DocSearch v2.0.1 - Verification Tests")
    print("=" * 60)
    
    test1_passed = test_case_sensitivity()
    test2_passed = test_batch_parsing()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✓ All tests PASSED - Package is working correctly!")
        return 0
    else:
        print("✗ Some tests FAILED - See output above")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
