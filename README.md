# DocSearch v2.0

A Python toolkit for document search and classification workflows with glob pattern filtering.

## Features

✓ **Multi-format support** - PDF, DOCX, Markdown, plain text  
✓ **Glob pattern filtering** - Process only files matching patterns  
✓ **Rich metadata extraction** - Page count, author, title, word count  
✓ **Batch processing** - Process hundreds of files efficiently  
✓ **Classification workflow** - Extract token previews for human/LLM review  
✓ **Explicit error handling** - Know exactly why a file couldn't be read  
✓ **Extensible** - Add custom readers for new formats  
✓ **CLI interface** - Command-line tools for common tasks

## Installation

```bash
# Basic installation (Markdown and text files only)
pip install docsearch

# With PDF support
pip install docsearch[pdf]

# With Word document support
pip install docsearch[docx]

# Full installation (all formats)
pip install docsearch[full]

# Development installation
pip install docsearch[dev]
```

Or install from source:

```bash
git clone https://github.com/ken/docsearch
cd docsearch
pip install -e .
```

## Quick Start

### Python API

```python
from docsearch import read_file

# Read a file
result = read_file("document.pdf")
if result.ok:
    print(result.text)
    print(f"Pages: {result.metadata.page_count}")
else:
    print(f"Error: {result.error}")

# Read preview (first 250 tokens)
from docsearch import read_file_preview

result = read_file_preview("large_doc.pdf", n_tokens=250)
print(result.text)

# Create batch for classification
from docsearch import create_labeled_batch_from_directory

batch_text = create_labeled_batch_from_directory(
    "/documents/invoices",
    categories=["invoice", "financial"],
    n_tokens=250
)
print(batch_text)
```

### Command Line

```bash
# Extract tokens from all files
docsearch extract /documents -o batch.md

# Extract only PDFs
docsearch extract /documents --glob "*.pdf" -o pdfs.md

# Extract multiple file types with categories
docsearch extract /invoices --glob "*.pdf,*.docx" \\
    --categories "invoice" -o batch.md

# Search for pattern in specific files
docsearch search /documents "invoice.*\\d+" --glob "*.pdf"

# Show file information
docsearch info document.pdf --tokens 100

# List supported formats
docsearch formats
```

## Glob Pattern Filtering

### Pattern Syntax

| Pattern | Meaning | Example |
|---------|---------|---------|
| `*` | Any characters except `/` | `*.pdf` |
| `**` | Any characters including `/` | `**/*.pdf` |
| `?` | Single character | `file?.pdf` |
| `[seq]` | Any character in seq | `file[123].pdf` |
| `[!seq]` | Any character not in seq | `file[!0-9].pdf` |

**Note:** Pattern matching is **case-sensitive** on all platforms. `*.pdf` will NOT match `file.PDF`.

### Pattern Examples

```bash
# Simple patterns
*.pdf                    # All PDF files
invoice_*.pdf            # PDFs starting with "invoice_"
report_?.pdf             # Single character after "report_"
data_[0-9]*.pdf          # Data files starting with digit

# Directory patterns
2024/*.pdf               # PDFs in any 2024 directory
2024/**/*.pdf            # PDFs in 2024 or subdirectories
**/invoices/*.pdf        # PDFs in any invoices directory

# Multiple patterns (comma-separated)
*.pdf,*.docx             # PDFs or DOCX files
invoice_*,receipt_*      # Invoices or receipts
```

### Glob Usage Examples

```bash
# Extract only PDFs
docsearch extract /documents --glob "*.pdf" -o batch.md

# Extract from specific subdirectory pattern
docsearch extract /documents --glob "**/2024/*.pdf" -o 2024_pdfs.md

# Multiple file types
docsearch extract /documents --glob "*.pdf,*.docx,*.txt" -o docs.md

# With categories and verbose output
docsearch extract /invoices --glob "INV_*.pdf" \\
    --categories "invoice,2024" -v -o invoices.md

# Search with filtering
docsearch search /documents "pattern" --glob "**/*.pdf"
```

## CLI Commands

### extract

Extract tokens from files for classification.

```bash
docsearch extract [OPTIONS] PATH

Options:
  -g, --glob PATTERN        Glob pattern to filter files
  -o, --output FILE         Output file (default: stdout)
  -a, --append              Append to output file
  -c, --categories CATS     Comma-separated categories
  -t, --tokens N            Tokens per file (default: 250)
  -r, --recursive           Process recursively (default)
  --no-recursive            Don't process subdirectories
  --file-list FILE          Read file paths from file
  -v, --verbose             Show verbose progress

Examples:
  docsearch extract /docs -o batch.md
  docsearch extract /docs --glob "*.pdf" -o pdfs.md
  docsearch extract /invoices --categories "invoice" -o batch.md
```

### search

Search files for regex patterns.

```bash
docsearch search [OPTIONS] PATH PATTERN

Options:
  -g, --glob PATTERN        Glob pattern to filter files
  -i, --ignore-case         Case-insensitive search
  -r, --recursive           Search recursively (default)
  --no-recursive            Don't search subdirectories
  -v, --verbose             Show verbose output

Examples:
  docsearch search /docs "invoice"
  docsearch search /docs "INV-\\d+" --glob "*.pdf"
  docsearch search /docs "pattern" -i --glob "**/2024/*"
```

### info

Show file information and preview.

```bash
docsearch info [OPTIONS] FILE

Options:
  -t, --tokens N            Tokens to preview (default: 100)

Examples:
  docsearch info document.pdf
  docsearch info large_file.docx --tokens 50
```

### formats

List supported file formats.

```bash
docsearch formats
```

## Python API Reference

### Reading Functions

```python
from docsearch import read_file, read_file_preview

# Read entire file
result = read_file("document.pdf")
# Returns: ReadResult with status, text, metadata, error

# Read preview (efficient for large files)
result = read_file_preview("document.pdf", n_tokens=250)
# Returns: ReadResult with truncated text
```

### Batch Processing

```python
from docsearch import (
    collect_files,
    create_batch_from_files,
    create_labeled_batch_from_directory,
    BatchBuilder
)

# Collect files from directory
files = collect_files("/documents", recursive=True)

# Create batch from files
batch = create_batch_from_files(
    files,
    categories=["invoice"],
    n_tokens=250
)

# Quick directory batch
batch_text = create_labeled_batch_from_directory(
    "/documents",
    categories=["invoice"],
    n_tokens=250,
    recursive=True
)

# Complex multi-source batch
builder = BatchBuilder()
builder.add_directory("/invoices", categories=["invoice"])
builder.add_directory("/receipts", categories=["receipt"])
batch_text = builder.to_format()
```

### Glob Filtering

```python
from docsearch import filter_files_by_glob, apply_glob_filter

# Filter files by pattern
files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
filtered = filter_files_by_glob(files, "*.pdf")
# Returns: ['/docs/a.pdf']

# Filter with multiple patterns
filtered = filter_files_by_glob(files, "*.pdf,*.docx")
# Returns: ['/docs/a.pdf', '/docs/b.docx']

# Filter with verbose output
filtered = apply_glob_filter(files, "*.pdf", verbose=True)
# Prints: Glob filter '*.pdf': 1/3 files matched
```

### Data Models

```python
from docsearch import ReadResult, ReadStatus, FileMetadata

# Check result status
if result.status == ReadStatus.SUCCESS:
    print("File read successfully")
elif result.status == ReadStatus.NOT_FOUND:
    print("File not found")
elif result.status == ReadStatus.CORRUPT_FILE:
    print("File is corrupt")

# Access metadata
print(f"Pages: {result.metadata.page_count}")
print(f"Author: {result.metadata.author}")
print(f"Words: {result.metadata.word_count}")
```

## Batch Format

The batch format is a structured text format for classification workflows:

```
<batch>
CATEGORIES: invoice, financial
<file>
FILEPATH: /documents/inv_001.pdf
FILENAME: inv_001.pdf
EXTENSION: .pdf
SIZE: 12345
TOKENS:
Invoice number: INV-2024-001
Date: January 15, 2024
Amount: $1,234.56
...
<file>
FILEPATH: /documents/inv_002.pdf
FILENAME: inv_002.pdf
EXTENSION: .pdf
SIZE: 23456
TOKENS:
Invoice number: INV-2024-002
...
```

### Parsing Batch Format

```python
from docsearch import BatchCollection

# Parse batch format
text = """<batch>
CATEGORIES: invoice
<file>
FILEPATH: /doc.pdf
FILENAME: doc.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Content here...
"""

collection = BatchCollection.from_format(text)

# Iterate over files
for categories, entry in collection.all_files():
    print(f"{entry.filename}: {categories}")
```

## Supported Formats

| Format | Extension | Reader | Dependencies |
|--------|-----------|--------|--------------|
| PDF | `.pdf` | PDFReader | `pypdf` |
| Word | `.docx` | DocxReader | `python-docx` |
| Markdown | `.md` | MarkdownReader | (built-in) |
| Plain Text | `.txt` | MarkdownReader | (built-in) |

### Adding Custom Readers

```python
from docsearch.readers import READER_REGISTRY, BaseReader
from docsearch.models import ReadResult, ReadStatus

class CustomReader:
    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.endswith('.custom')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        # Your reading logic here
        ...

# Register reader
READER_REGISTRY['.custom'] = CustomReader
```

## Error Handling

DocSearch uses explicit error states instead of exceptions:

```python
result = read_file("document.pdf")

if result.ok:
    # Success
    process(result.text)
else:
    # Handle error
    if result.status == ReadStatus.NOT_FOUND:
        print("File doesn't exist")
    elif result.status == ReadStatus.PERMISSION_DENIED:
        print("Permission denied")
    elif result.status == ReadStatus.CORRUPT_FILE:
        print(f"Corrupt file: {result.error}")
    else:
        print(f"Error: {result.error}")
```

## Practical Examples

### Build Classification Batch

```bash
# Extract PDFs from multiple directories with labels
docsearch extract /accounting/invoices --glob "*.pdf" \\
    --categories "invoice" -o batch.md

docsearch extract /accounting/receipts --glob "*.pdf" \\
    --categories "receipt" -a -o batch.md

docsearch extract /legal/contracts --glob "*.pdf" \\
    --categories "contract" -a -o batch.md
```

### Extract Recent Files

```bash
# Extract all 2024 documents
docsearch extract /documents --glob "**/2024/**/*.pdf" \\
    --categories "2024" -v -o 2024_docs.md
```

### Search Specific File Types

```bash
# Search only in Word documents
docsearch search /documents "contract" --glob "*.docx"

# Search in PDFs from specific year
docsearch search /documents "invoice" --glob "**/2024/*.pdf"
```

### Process File List

```bash
# Create file list
cat > files.txt << EOF
/docs/file1.pdf
/docs/file2.pdf
/docs/file3.pdf
EOF

# Process list
docsearch extract --file-list files.txt -o batch.md
```

## Performance

- **Token preview**: Efficiently extracts first N tokens without reading entire file
- **Glob filtering**: Files filtered before reading (fast)
- **Batch processing**: Can process thousands of files
- **Parallel ready**: Architecture supports parallel processing

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=docsearch --cov-report=term-missing

# Verbose
pytest -v
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Changelog

### v2.0.0 (Current)

- ✨ Added glob pattern filtering
- ✨ Integrated glob support into CLI
- ✨ Added `--glob` parameter to extract and search commands
- 📚 Comprehensive glob pattern documentation
- 🧪 Tests for glob matching

### v1.0.0

- Initial release
- Multi-format support (PDF, DOCX, Markdown)
- Batch processing
- Classification workflow support
- Rich metadata extraction
- Explicit error handling
- CLI interface

## Support

For bugs and feature requests, please open an issue on GitHub.

For questions, see the documentation or examples above.

---

**Made with ❤️ by Ken**
