# DocSearch Cheatsheet

Quick reference for common tasks. For complete documentation, see [API.md](API.md).

---

## Installation

```bash
pip install docsearch[full]     # Everything
pip install docsearch[pdf]      # Just PDF support
pip install docsearch[docx]     # Just Word support
```

---

## Python API - Quick Reference

### Read a File

```python
from docsearch import read_file

result = read_file("document.pdf")
if result.ok:
    print(result.text)
    print(f"Pages: {result.metadata.page_count}")
```

### Read Preview (Fast)

```python
from docsearch import read_file_preview

result = read_file_preview("large_doc.pdf", n_tokens=100)
print(result.text)  # First 100 tokens only
```

### Glob Matching

```python
from docsearch import glob_matches

glob_matches("/docs/file.pdf", "*.pdf")          # True
glob_matches("/docs/file.PDF", "*.pdf")          # False (case-sensitive!)
glob_matches("/docs/2024/file.pdf", "2024/*.pdf")  # True
```

### Filter Files

```python
from docsearch import filter_files_by_glob

files = ["/a.pdf", "/b.docx", "/c.txt"]
pdfs = filter_files_by_glob(files, "*.pdf")      # ["/a.pdf"]
docs = filter_files_by_glob(files, "*.pdf,*.docx")  # ["/a.pdf", "/b.docx"]
```

### Metadata Search (NEW in v2.1.0)

```python
from docsearch import search_metadata, filter_by_name_pattern

# Search filenames (fast - no file reading)
files = ['/docs/invoice_2024.pdf', '/docs/report.pdf']

# Get matches with positions
matches = search_metadata(files, '2024')
# Returns: [('/docs/invoice_2024.pdf', (14, 18))]

# Simple filter
invoices = filter_by_name_pattern(files, 'invoice', case_sensitive=False)
# Returns: ['/docs/invoice_2024.pdf']

# Detailed results
from docsearch import search_metadata_dict
result = search_metadata_dict(files, r'_\d{4}')
print(result['matched_files'])  # 1
```

### File Metadata Search (NEW in v2.2.0)

```python
from docsearch import filter_by_date, filter_by_size, filter_by_pdf_metadata

# Filter by date
recent = filter_by_date(files, modified_after='2024-01-01')

# Filter by size
large = filter_by_size(files, min_bytes=1_000_000)  # > 1 MB

# Filter PDFs by author
docs = filter_by_pdf_metadata(files, author='John Doe')

# Combined filters
from docsearch import FileMetadataFilter, search_by_metadata
criteria = FileMetadataFilter(
    extensions=['.pdf'],
    modified_after='2024-01-01',
    size_min=1_000_000
)
matches = search_by_metadata(files, criteria)
```

### Create Batch

```python
from docsearch import create_labeled_batch_from_directory

batch = create_labeled_batch_from_directory(
    "/documents",
    categories=["invoice"],
    n_tokens=250
)
```

### Build Complex Batch

```python
from docsearch import BatchBuilder

builder = BatchBuilder()
builder.add_directory("/invoices", categories=["invoice"])
builder.add_directory("/receipts", categories=["receipt"])
batch_text = builder.to_format()
```

### Parse Batch

```python
from docsearch import BatchCollection

collection = BatchCollection.from_format(text)
for categories, entry in collection.all_files():
    print(f"{entry.filename}: {categories}")
```

---

## CLI - Quick Reference

### Extract Commands

```bash
# Basic
docsearch extract /docs -o batch.md

# Only PDFs
docsearch extract /docs --glob "*.pdf" -o batch.md

# Multiple types
docsearch extract /docs --glob "*.pdf,*.docx" -o batch.md

# With categories
docsearch extract /docs --categories "invoice,2024" -o batch.md

# Verbose (show stats)
docsearch extract /docs --glob "*.pdf" -v -o batch.md

# Custom tokens
docsearch extract /docs --tokens 500 -o batch.md

# Append to file
docsearch extract /docs --glob "*.pdf" -a -o batch.md

# From file list
docsearch extract --file-list paths.txt -o batch.md
```

### Search Commands

```bash
# Basic search
docsearch search /docs "invoice"

# Only in PDFs
docsearch search /docs "invoice" --glob "*.pdf"

# Case-insensitive
docsearch search /docs "invoice" -i

# Regex
docsearch search /docs "INV-\d+" --glob "*.pdf"

# Specific directory pattern
docsearch search /docs "contract" --glob "**/2024/*.pdf"

# Verbose (shows files as searched)
docsearch search /docs "pattern" --glob "*.md" -v

# METADATA-ONLY (NEW in v2.1.0 - fast filename search)
docsearch search /docs "2024" --metadata-only
docsearch search /docs "invoice" --metadata-only -i
docsearch search /docs "_\d{4}_" --metadata-only
```

**Understanding Search Output:**
```
Total: 26 matches in 15/140 files
```
- **26 matches** = Total pattern occurrences found
- **15** = Number of files that contain matches
- **140** = Total number of files searched

**Metadata-Only Output:**
```
Matched files:
  /docs/invoice_[2024]_001.pdf
  /docs/report_[2024]_final.docx

Total: 2 files matched (out of 140 searched)
```

Only files with matches are displayed. Use `-v` to see all files as they're searched.

### Info Command

```bash
docsearch info document.pdf
docsearch info document.pdf --tokens 50
```

### List Formats

```bash
docsearch formats
```

---

## Glob Patterns - Quick Reference

### Basic Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `*.pdf` | All PDFs | `file.pdf`, `doc.pdf` |
| `invoice_*` | Files starting with "invoice_" | `invoice_001.pdf` |
| `*_2024.pdf` | Files ending with "_2024.pdf" | `report_2024.pdf` |
| `file?.pdf` | Single char after "file" | `file1.pdf`, `fileA.pdf` |

### Recursive Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `**/*.pdf` | PDFs anywhere | `/a/b/file.pdf` |
| `2024/**/*.pdf` | PDFs in/under 2024 | `/docs/2024/Q1/file.pdf` |
| `**/invoices/*.pdf` | PDFs in any invoices dir | `/any/path/invoices/file.pdf` |

### Character Classes

| Pattern | Matches | Example |
|---------|---------|---------|
| `file[0-9]*` | Files with digit | `file1.pdf`, `file2.pdf` |
| `file[A-Z]*` | Files with capital | `fileA.pdf`, `fileB.pdf` |
| `file[!0-9]*` | Files without digit | `fileA.pdf`, `file_.pdf` |

### Multiple Patterns

```bash
--glob "*.pdf,*.docx,*.txt"     # PDFs, DOCX, or TXT files
--glob "invoice_*,receipt_*"    # Invoices or receipts
```

### Important

**Glob matching is CASE-SENSITIVE on all platforms:**
- `*.pdf` matches `file.pdf` ✓
- `*.pdf` does NOT match `file.PDF` ✗

---

## Error Handling - Quick Reference

### Check Success

```python
result = read_file("doc.pdf")

if result.ok:
    # Success
    print(result.text)
else:
    # Error
    print(result.error)
```

### Handle Specific Errors

```python
from docsearch import ReadStatus

if result.status == ReadStatus.NOT_FOUND:
    print("File doesn't exist")
elif result.status == ReadStatus.CORRUPT_FILE:
    print("File is damaged")
elif result.status == ReadStatus.PERMISSION_DENIED:
    print("Permission denied")
```

### Error Status Values

| Status | Meaning |
|--------|---------|
| `SUCCESS` | Worked |
| `NOT_FOUND` | File doesn't exist |
| `PERMISSION_DENIED` | No permission |
| `UNSUPPORTED_FORMAT` | Wrong file type |
| `CORRUPT_FILE` | File damaged |
| `EMPTY_FILE` | No content |
| `READ_ERROR` | Other error |

---

## Common Workflows

### Workflow 1: Extract PDFs from 2024

```bash
docsearch extract /documents \
    --glob "**/2024/**/*.pdf" \
    --categories "2024,document" \
    -v -o 2024_docs.md
```

### Workflow 2: Build Classification Batch

```bash
# Invoices
docsearch extract /accounting/invoices \
    --glob "*.pdf" \
    --categories "invoice" \
    -o batch.md

# Receipts (append)
docsearch extract /accounting/receipts \
    --glob "*.pdf" \
    --categories "receipt" \
    -a -o batch.md

# Contracts (append)
docsearch extract /legal/contracts \
    --glob "*.pdf" \
    --categories "contract" \
    -a -o batch.md
```

### Workflow 3: Search and Extract

```bash
# Find matching files
docsearch search /docs "INV-2024" --glob "*.pdf" > found.txt

# Extract for review
docsearch extract /docs \
    --glob "INV-2024-*.pdf" \
    -o review.md
```

### Workflow 4: Multi-Source Batch (Python)

```python
from docsearch import BatchBuilder

builder = BatchBuilder()
builder.add_directory("/invoices", categories=["invoice"])
builder.add_directory("/receipts", categories=["receipt"])  
builder.add_files(["/c1.pdf", "/c2.pdf"], categories=["contract"])

with open("batch.md", "w") as f:
    f.write(builder.to_format())
```

### Workflow 5: Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from docsearch import read_file_preview

files = ["/f1.pdf", "/f2.pdf", "/f3.pdf"]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(
        lambda f: read_file_preview(f, 250),
        files
    ))

for result in results:
    if result.ok:
        process(result.text)
```

---

## Troubleshooting

### No files matched

```bash
# Use verbose to see stats
docsearch extract /docs --glob "*.pdf" -v
# Output: Glob filter '*.pdf': 0/156 files matched

# Check case sensitivity
docsearch extract /docs --glob "*.PDF" -v  # Try uppercase
```

### Module not found

```bash
# Missing pypdf
pip install pypdf

# Missing python-docx
pip install python-docx

# Install everything
pip install docsearch[full]
```

### Empty extraction

```python
# Check file status
result = read_file("document.pdf")
print(result.status)  # Shows why it failed
print(result.error)   # Error message
```

### Permission errors

```bash
# Check file permissions
ls -l document.pdf

# May need sudo or different user
```

---

## Performance Tips

1. **Use previews** for classification (faster)
   ```python
   result = read_file_preview("doc.pdf", n_tokens=250)
   ```

2. **Filter early** with glob patterns
   ```python
   files = collect_files("/docs")
   pdfs = filter_files_by_glob(files, "*.pdf")  # Filter before processing
   ```

3. **Parallel processing** for many files
   ```python
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(read_file, files)
   ```

4. **Non-recursive** if only need top level
   ```bash
   docsearch extract /docs --no-recursive
   ```

---

## Batch Format Structure

```
<batch>
CATEGORIES: category1, category2
<file>
FILEPATH: /path/to/file.pdf
FILENAME: file.pdf
EXTENSION: .pdf
SIZE: 12345
TOKENS:
Content here...
<file>
FILEPATH: /path/to/another.docx
...
```

---

## Quick Tests

### Test Glob Matching

```python
from docsearch import glob_matches

# Should be True
assert glob_matches("/docs/file.pdf", "*.pdf")

# Should be False (case-sensitive)
assert not glob_matches("/docs/file.PDF", "*.pdf")

# Should be True
assert glob_matches("/docs/2024/file.pdf", "2024/*.pdf")
```

### Test File Reading

```python
from docsearch import read_file

result = read_file("test.pdf")
assert result.ok or result.error  # Always has status
```

### Test CLI

```bash
# Should show help
docsearch --help

# Should list formats
docsearch formats

# Should show file info
docsearch info test.pdf
```

---

## Supported Formats

| Extension | Reader | Install |
|-----------|--------|---------|
| `.pdf` | PDFReader | `pip install pypdf` |
| `.docx` | DocxReader | `pip install python-docx` |
| `.md` | MarkdownReader | Built-in |
| `.txt` | MarkdownReader | Built-in |

---

## Links

- **[README.md](README.md)** - Full documentation
- **[API.md](API.md)** - Complete API reference
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[BUGFIXES.md](BUGFIXES.md)** - Known issues

---

## One-Liners

```bash
# Extract all PDFs
docsearch extract /docs --glob "*.pdf" -o batch.md

# Search in Word docs
docsearch search /docs "pattern" --glob "*.docx"

# Metadata-only search (fast)
docsearch search /docs "2024" --metadata-only

# Get file info
docsearch info file.pdf

# List formats
docsearch formats

# Extract with categories
docsearch extract /docs --categories "invoice" -o batch.md

# Verbose extraction
docsearch extract /docs --glob "*.pdf" -v -o batch.md

# Extract from 2024
docsearch extract /docs --glob "**/2024/*.pdf" -o 2024.md

# Multiple types
docsearch extract /docs --glob "*.pdf,*.docx" -o docs.md

# Find files by name (fast)
docsearch search /docs "invoice" --metadata-only -i
```

---

**Version:** 2.2.0  
**Last Updated:** April 5, 2026

For complete documentation, see [API.md](API.md) and [README.md](README.md).
