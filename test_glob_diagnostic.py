"""
Diagnostic script to check glob_matches behavior on Windows.
Run this to see what's happening.
"""

import platform
import sys

print(f"Platform: {platform.system()}")
print(f"Python: {sys.version}")
print()

# Test the function
from docsearch.glob_filter import glob_matches

test_cases = [
    ("/docs/file.pdf", "*.pdf", True, "lowercase file, lowercase pattern"),
    ("/docs/file.PDF", "*.PDF", True, "uppercase file, uppercase pattern"),
    ("/docs/file.PDF", "*.pdf", None, "uppercase file, lowercase pattern (platform-dependent)"),
    ("/docs/file.pdf", "*.PDF", None, "lowercase file, uppercase pattern (platform-dependent)"),
]

print("Testing glob_matches:")
print("-" * 70)

for filepath, pattern, expected, description in test_cases:
    result = glob_matches(filepath, pattern)
    
    if expected is None:
        # Platform dependent
        if platform.system() == 'Windows':
            expected = True
            expected_str = "True (Windows)"
        else:
            expected = False
            expected_str = "False (Linux/Mac)"
    else:
        expected_str = str(expected)
    
    status = "✓" if result == expected else "✗ FAIL"
    
    print(f"{status} {description}")
    print(f"   glob_matches('{filepath}', '{pattern}') = {result}")
    print(f"   Expected: {expected_str}")
    if result != expected:
        print(f"   >>> THIS IS THE PROBLEM! <<<")
    print()

print("-" * 70)
print()
print("If you see failures above, the glob_filter.py file may not be updated correctly.")
print("Make sure you replaced the file with the latest version.")
