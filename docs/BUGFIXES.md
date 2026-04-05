# DocSearch v2.0.1 - Bugfixes

## Issues Fixed

### 1. Case-Insensitive Matching on Windows (CRITICAL)

**Issue:** `AssertionError: assert not True` - Pattern `*.pdf` matched `file.PDF` on Windows

**Location:** `docsearch/glob_filter.py`, line 57

**Problem:** The `fnmatch.fnmatch()` function is case-insensitive on Windows, causing `*.pdf` to incorrectly match `file.PDF`. This breaks cross-platform consistency.

**Fix:**
```python
# OLD (PLATFORM-DEPENDENT):
if '/' not in pattern:
    filename = filepath.split('/')[-1]
    return fnmatch.fnmatch(filename, pattern)  # ❌ Case-insensitive on Windows

# NEW (CONSISTENT):
if '/' not in pattern:
    filename = filepath.split('/')[-1]
    return fnmatch.fnmatchcase(filename, pattern)  # ✓ Case-sensitive everywhere
```

**Impact:** 
- Glob patterns now behave identically on Windows, Linux, and macOS
- `*.pdf` matches `file.pdf` but NOT `file.PDF` on all platforms
- Users get predictable, case-sensitive matching

---

### 2. Batch Parsing Error (CRITICAL)

**Issue:** `AttributeError: 'dict' object has no attribute 'tokens'`

**Location:** `docsearch/models.py`, line 140

**Problem:** When parsing multiple files in a batch, the code tried to set `current_file.tokens` but `current_file` is a dictionary, not a BatchEntry object.

**Fix:**
```python
# OLD (BROKEN):
elif stripped == '<file>':
    if current_file:
        current_file.tokens = '\n'.join(tokens_lines)  # ❌ dict has no .tokens
        current_batch.files.append(current_file)

# NEW (FIXED):
elif stripped == '<file>':
    if current_file:
        current_file['tokens'] = '\n'.join(tokens_lines)  # ✓ dict assignment
        entry = BatchEntry(**current_file)                 # ✓ create object
        current_batch.files.append(entry)
```

**Impact:** BatchCollection.from_format() now correctly parses batches with multiple files.

---

### 2. Batch Parsing Error (CRITICAL)

**Issue:** `AttributeError: 'dict' object has no attribute 'tokens'`

**Location:** `docsearch/models.py`, line 140

**Problem:** When parsing multiple files in a batch, the code tried to set `current_file.tokens` but `current_file` is a dictionary, not a BatchEntry object.

**Fix:**
```python
# OLD (BROKEN):
elif stripped == '<file>':
    if current_file:
        current_file.tokens = '\n'.join(tokens_lines)  # ❌ dict has no .tokens
        current_batch.files.append(current_file)

# NEW (FIXED):
elif stripped == '<file>':
    if current_file:
        current_file['tokens'] = '\n'.join(tokens_lines)  # ✓ dict assignment
        entry = BatchEntry(**current_file)                 # ✓ create object
        current_batch.files.append(entry)
```

**Impact:** BatchCollection.from_format() now correctly parses batches with multiple files.

---

### 3. Test Suite Update (MINOR)

**Issue:** Test needed to verify case-sensitive behavior

**Location:** `tests/test_docsearch.py`

**Change:** Updated `test_case_sensitivity()` to properly test case-sensitive matching on all platforms.

```python
def test_case_sensitivity(self):
    """Test case-sensitive matching."""
    assert glob_matches("/docs/file.pdf", "*.pdf")    # lowercase matches
    assert glob_matches("/docs/file.PDF", "*.PDF")    # uppercase matches
    assert not glob_matches("/docs/file.pdf", "*.PDF")  # different case = no match
```

---

## Verification

All three fixes verified:

```bash
cd docsearch-v2.0

# Test 1: Case-sensitive matching
python -c "
from docsearch import glob_matches
assert glob_matches('/docs/file.pdf', '*.pdf')
assert not glob_matches('/docs/file.pdf', '*.PDF')
print('✓ Case-sensitive matching works!')
"

# Test 2: Batch parsing with multiple files
python -c "
from docsearch.models import BatchCollection
text = '''<batch>
CATEGORIES: test
<file>
FILEPATH: /test1.pdf
FILENAME: test1.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Content 1
<file>
FILEPATH: /test2.pdf
FILENAME: test2.pdf
EXTENSION: .pdf
SIZE: 5678
TOKENS:
Content 2
'''
collection = BatchCollection.from_format(text)
assert len(collection.batches[0].files) == 2
print('✓ Batch parsing works!')
"
```

Output:
```
✓ Case-sensitive matching works!
✓ Batch parsing works!
```

---

## Files Modified

1. `docsearch/glob_filter.py` - Changed `fnmatch.fnmatch()` to `fnmatch.fnmatchcase()` for case-sensitive matching
2. `docsearch/models.py` - Fixed BatchEntry creation in from_format()
3. `tests/test_docsearch.py` - Updated case sensitivity test to verify correct behavior

---

## Upgrade Instructions

If you have v2.0.0 installed:

### Option 1: Re-download

Download the updated `docsearch-v2.0.tar.gz` and reinstall:

```bash
tar -xzf docsearch-v2.0.tar.gz
cd docsearch-v2.0
pip install -e .
```

### Option 2: Apply Patch Manually

Edit `docsearch/models.py` around line 137:

```python
# Find this line:
            elif stripped == '<file>':
                if current_file:
                    current_file.tokens = '\n'.join(tokens_lines)
                    current_batch.files.append(current_file)

# Replace with:
            elif stripped == '<file>':
                if current_file:
                    current_file['tokens'] = '\n'.join(tokens_lines)
                    entry = BatchEntry(**current_file)
                    current_batch.files.append(entry)
```

Edit `tests/test_docsearch.py` around line 38:

```python
# Replace test_case_sensitivity method with:
    def test_case_sensitivity(self):
        """Test case-sensitive matching."""
        assert glob_matches("/docs/file.pdf", "*.pdf")
        assert glob_matches("/docs/file.PDF", "*.PDF")
        assert not glob_matches("/docs/file.pdf", "*.PDF")
```

---

## Test Results

After fixes, all tests pass:

```
tests/test_docsearch.py::TestGlobMatching::test_simple_patterns PASSED
tests/test_docsearch.py::TestGlobMatching::test_recursive_patterns PASSED
tests/test_docsearch.py::TestGlobMatching::test_character_classes PASSED
tests/test_docsearch.py::TestGlobMatching::test_case_sensitivity PASSED  ✓ FIXED
tests/test_docsearch.py::TestFileFiltering::test_single_pattern PASSED
tests/test_docsearch.py::TestFileFiltering::test_multiple_patterns PASSED
tests/test_docsearch.py::TestFileFiltering::test_no_pattern PASSED
tests/test_docsearch.py::TestBatchFormat::test_parse_simple_batch PASSED
tests/test_docsearch.py::TestBatchFormat::test_parse_multiple_files PASSED  ✓ FIXED
tests/test_docsearch.py::TestReadResult::test_ok_property PASSED

========== 10 passed in 0.5s ==========
```

---

**Version:** 2.0.1  
**Date:** February 16, 2026  
**Status:** All tests passing
