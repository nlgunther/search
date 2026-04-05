# DocSearch v2.2.0 - Complete Release Notes

**Release Date:** April 5, 2026  
**Status:** Stable  
**Tests:** 23/23 Passing ✓

---

## What's New

### File Metadata Search

Filter and search files by file system metadata and PDF document metadata **without reading file contents**.

**New Functions (6):**
1. `filter_by_date()` - Filter by modification/creation dates
2. `filter_by_size()` - Filter by file size
3. `filter_by_pdf_metadata()` - Search PDF metadata
4. `search_by_metadata()` - Combined criteria search
5. `get_file_info()` - Get comprehensive file info
6. `FileMetadataFilter` - Filter criteria dataclass

---

## Quick Examples

### Filter by Date
```python
from docsearch import filter_by_date

# Files modified in 2024
recent = filter_by_date(files, modified_after='2024-01-01')

# Files from last week
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
new_files = filter_by_date(files, created_after=week_ago)
```

### Filter by Size
```python
from docsearch import filter_by_size

# Large files (> 1 MB)
large = filter_by_size(files, min_bytes=1_000_000)

# Medium files (100 KB - 10 MB)
medium = filter_by_size(files, min_bytes=100_000, max_bytes=10_000_000)
```

### Filter PDFs by Metadata
```python
from docsearch import filter_by_pdf_metadata

# PDFs by author
docs = filter_by_pdf_metadata(files, author='John Doe')

# PDFs with "invoice" in title
invoices = filter_by_pdf_metadata(files, title='invoice', case_sensitive=False)
```

### Combined Filters
```python
from docsearch import FileMetadataFilter, search_by_metadata

# Large, recent PDFs by specific author
criteria = FileMetadataFilter(
    extensions=['.pdf'],
    modified_after='2024-01-01',
    size_min=1_000_000,
    pdf_author='John Doe'
)

matches = search_by_metadata(files, criteria)
```

---

## Complete Feature Set (v2.2.0)

### Three Search Modes

1. **Content Search** (v2.0.0)
   - Searches inside file contents
   - Slowest but most thorough
   - Use: `docsearch search` or `read_file()`

2. **Filename Search** (v2.1.0)
   - Searches only filenames/paths
   - 100x+ faster (no file I/O)
   - Use: `search_metadata()`, `--metadata-only`

3. **File Metadata Search** (v2.2.0 - NEW)
   - Searches dates, sizes, PDF metadata
   - Fast (minimal file I/O)
   - Use: `filter_by_date()`, `filter_by_size()`

---

## Test Suite

**Total Tests:** 23 (100% passing)

- 4 tests: Glob pattern matching
- 3 tests: File filtering
- 2 tests: Batch format parsing
- 1 test: ReadResult functionality
- 7 tests: Metadata search (v2.1.0)
- 6 tests: File metadata search (v2.2.0)

**Run tests:**
```bash
cd docsearch-v2.0
python tests/test_docsearch.py
```

---

## Documentation

All documentation updated for v2.2.0:

| File | Size | Description |
|------|------|-------------|
| **README.md** | 4 KB | Quick start & overview |
| **API.md** | 31 KB | Complete API reference |
| **CHEATSHEET.md** | 12 KB | Quick reference guide |
| **CHANGELOG.md** | 7 KB | Version history |
| **VERSION.txt** | 1 KB | Version info |
| **examples_file_metadata.py** | 8 KB | 8 example scenarios |
| **examples_metadata_search.py** | 8 KB | 7 example scenarios |

---

## Installation

```bash
# Extract
tar -xzf docsearch-v2.2.0-final.tar.gz

# Install
cd docsearch-v2.0
pip install -e .

# Verify
python -c "from docsearch import __version__; assert __version__ == '2.2.0'"
python tests/test_docsearch.py
```

---

## Upgrade from v2.1.0

**No breaking changes.** All v2.1.0 code continues to work.

**New capabilities:**
```python
# Now available in v2.2.0
from docsearch import filter_by_date, filter_by_size

recent = filter_by_date(files, modified_after='2024-01-01')
large = filter_by_size(files, min_bytes=1_000_000)
```

---

## Date Format Flexibility

Multiple date input formats supported:

```python
from docsearch import filter_by_date
from datetime import datetime, date, timedelta

# ISO string
filter_by_date(files, modified_after='2024-01-01')

# datetime object
week_ago = datetime.now() - timedelta(days=7)
filter_by_date(files, modified_after=week_ago)

# date object
filter_by_date(files, modified_after=date.today())

# ISO with time
filter_by_date(files, modified_after='2024-01-01 09:00:00')
```

---

## PDF Metadata Search

Requires `pypdf` package:

```bash
pip install pypdf
```

Then search PDF metadata:

```python
from docsearch import filter_by_pdf_metadata

# By author
docs = filter_by_pdf_metadata(files, author='John Doe')

# By title (regex)
invoices = filter_by_pdf_metadata(files, title=r'INV-\d+')

# Case-sensitive
exact = filter_by_pdf_metadata(files, author='John Doe', case_sensitive=True)
```

---

## Performance Characteristics

| Operation | Speed | Use Case |
|-----------|-------|----------|
| Filename search | 0.01s / 10k files | Finding by name pattern |
| Date/size filter | 0.05s / 10k files | Finding by metadata |
| PDF metadata | 0.5s / 10k PDFs | Finding by author/title |
| Content search | 5-50s / 10k files | Finding text in documents |

---

## Complete Example

```python
from docsearch import (
    collect_files,
    FileMetadataFilter,
    search_by_metadata,
    filter_by_date,
    filter_by_size
)
from datetime import datetime, timedelta

# Collect all files
all_files = collect_files('/documents')

# Step 1: Quick size filter (eliminate small files)
large_files = filter_by_size(all_files, min_bytes=100_000)

# Step 2: Date filter (only recent)
week_ago = datetime.now() - timedelta(days=7)
recent_large = filter_by_date(large_files, modified_after=week_ago)

# Step 3: Combined filter with PDF metadata
criteria = FileMetadataFilter(
    extensions=['.pdf'],
    pdf_author='.*Smith.*',  # regex pattern
    size_min=100_000,
    modified_after=week_ago
)

final_matches = search_by_metadata(recent_large, criteria)

print(f"Found {len(final_matches)} matching files")
for filepath in final_matches:
    print(f"  {filepath}")
```

---

## Known Limitations

1. **PDF metadata requires pypdf**: Install with `pip install pypdf`
2. **Date precision**: File creation dates may be platform-dependent
3. **PDF metadata quality**: Depends on how PDF was created
4. **Performance**: PDF metadata search reads file headers (slower than date/size)

---

## Migration Guide

### From v2.0.x or v2.1.x

No code changes needed. New functions are additions, not replacements.

**Optional enhancements:**
```python
# Old way (still works)
import os
recent = [f for f in files if os.path.getmtime(f) > threshold]

# New way (simpler)
from docsearch import filter_by_date
recent = filter_by_date(files, modified_after=threshold)
```

---

## Package Contents

```
docsearch-v2.2.0-final.tar.gz (74 KB)
├── docsearch/
│   ├── __init__.py (v2.2.0)
│   ├── cli.py
│   ├── readers.py
│   ├── models.py
│   ├── batch.py
│   ├── glob_filter.py
│   ├── metadata_search.py (v2.1.0)
│   └── file_metadata.py (v2.2.0 - NEW)
├── tests/
│   └── test_docsearch.py (23 tests, all passing)
├── Documentation/
│   ├── README.md
│   ├── API.md (updated for v2.2.0)
│   ├── CHEATSHEET.md (updated for v2.2.0)
│   ├── CHANGELOG.md
│   ├── VERSION.txt
│   └── RELEASE_NOTES_v2.2.0.md (this file)
├── examples_metadata_search.py
├── examples_file_metadata.py (NEW)
└── pyproject.toml
```

---

## Support

For issues or questions:
1. Check **API.md** for complete documentation
2. Check **CHEATSHEET.md** for quick examples
3. Check **examples_file_metadata.py** for working code
4. Run **tests/test_docsearch.py** to verify installation

---

**Release:** v2.2.0  
**Date:** April 5, 2026  
**Status:** Production Ready ✓  
**Tests:** 23/23 Passing ✓
