# DocSearch API Documentation

Complete API reference for the docsearch package v2.0.1.

## Table of Contents

- [Installation](#installation)
- [Core Reading Functions](#core-reading-functions)
- [Data Models](#data-models)
- [Batch Processing](#batch-processing)
- [Glob Pattern Filtering](#glob-pattern-filtering)
- [CLI Commands](#cli-commands)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)

---

## Installation

```bash
# Basic installation
pip install docsearch

# With PDF support
pip install docsearch[pdf]

# With Word document support  
pip install docsearch[docx]

# Full installation (all formats)
pip install docsearch[full]
```

---

## Core Reading Functions

### read_file()

Read a complete file and return structured result.

```python
from docsearch import read_file

def read_file(filepath: str) -> ReadResult
```

**Parameters:**
- `filepath` (str): Path to file to read

**Returns:**
- `ReadResult`: Object containing status, text, metadata, and any errors

**Example:**
```python
from docsearch import read_file

result = read_file("document.pdf")

if result.ok:
    print(f"Read {len(result.text)} characters")
    print(f"Pages: {result.metadata.page_count}")
    print(f"Author: {result.metadata.author}")
else:
    print(f"Error: {result.error}")
    print(f"Status: {result.status}")
```

**Supported Formats:**
- PDF (`.pdf`) - requires `pypdf`
- Word (`.docx`) - requires `python-docx`
- Markdown (`.md`) - built-in
- Plain text (`.txt`) - built-in

---

### read_file_preview()

Read only the first N tokens from a file (efficient for large files).

```python
from docsearch import read_file_preview

def read_file_preview(filepath: str, n_tokens: int = 250) -> ReadResult
```

**Parameters:**
- `filepath` (str): Path to file to read
- `n_tokens` (int, optional): Number of tokens to extract. Default: 250

**Returns:**
- `ReadResult`: Object with truncated text content

**Example:**
```python
from docsearch import read_file_preview

# Get first 100 tokens for preview
result = read_file_preview("large_document.pdf", n_tokens=100)

if result.ok:
    print("Preview:", result.text)
    print(f"Full document has {result.metadata.page_count} pages")
```

**Use Cases:**
- Quick content preview
- Classification workflows (extract sample for categorization)
- Large file processing (avoid reading entire file)
- Batch processing (faster when full content not needed)

---

### get_supported_formats()

Get dictionary of supported file formats and their readers.

```python
from docsearch import get_supported_formats

def get_supported_formats() -> Dict[str, str]
```

**Returns:**
- `Dict[str, str]`: Mapping of file extensions to reader class names

**Example:**
```python
from docsearch import get_supported_formats

formats = get_supported_formats()
for ext, reader in formats.items():
    print(f"{ext}: {reader}")

# Output:
# .pdf: PDFReader
# .docx: DocxReader
# .md: MarkdownReader
# .txt: MarkdownReader
```

---

### get_reader()

Get the appropriate reader class for a file.

```python
from docsearch import get_reader

def get_reader(filepath: str) -> Optional[Type[BaseReader]]
```

**Parameters:**
- `filepath` (str): Path to file

**Returns:**
- Reader class if supported, `None` if unsupported format

**Example:**
```python
from docsearch import get_reader

reader = get_reader("document.pdf")
if reader:
    result = reader.read("document.pdf")
    print(result.text)
else:
    print("Unsupported file format")
```

---

## Data Models

### ReadResult

Result object returned by all reading operations.

```python
@dataclass
class ReadResult:
    filepath: str                    # Path to file that was read
    status: ReadStatus              # Success/error status
    text: str = ""                  # Extracted text content
    metadata: FileMetadata = ...    # Document metadata
    error: Optional[str] = None     # Error message if failed
    
    @property
    def ok(self) -> bool:           # True if status == SUCCESS
        ...
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `filepath` | str | Path to the file |
| `status` | ReadStatus | Status enum value |
| `text` | str | Extracted text content |
| `metadata` | FileMetadata | Document metadata |
| `error` | str or None | Error message if failed |
| `ok` | bool | True if read succeeded |

**Example:**
```python
result = read_file("document.pdf")

# Check if successful
if result.ok:
    process_text(result.text)
else:
    # Handle specific error types
    if result.status == ReadStatus.NOT_FOUND:
        print("File doesn't exist")
    elif result.status == ReadStatus.CORRUPT_FILE:
        print(f"File is corrupt: {result.error}")
    else:
        print(f"Error: {result.error}")
```

---

### ReadStatus

Enum defining all possible read outcomes.

```python
class ReadStatus(Enum):
    SUCCESS = "success"                    # File read successfully
    NOT_FOUND = "not_found"               # File doesn't exist
    PERMISSION_DENIED = "permission_denied"  # No read permission
    UNSUPPORTED_FORMAT = "unsupported_format"  # File type not supported
    CORRUPT_FILE = "corrupt_file"         # File is damaged/corrupt
    EMPTY_FILE = "empty_file"             # File has no content
    READ_ERROR = "read_error"             # Other read error
```

**Usage:**
```python
from docsearch import ReadStatus

result = read_file("document.pdf")

# Pattern matching (Python 3.10+)
match result.status:
    case ReadStatus.SUCCESS:
        print("Success!")
    case ReadStatus.NOT_FOUND:
        print("File not found")
    case ReadStatus.CORRUPT_FILE:
        print("File is corrupt")
    case _:
        print(f"Error: {result.error}")
```

---

### FileMetadata

Metadata extracted from documents.

```python
@dataclass
class FileMetadata:
    page_count: Optional[int] = None      # Number of pages (PDF)
    word_count: Optional[int] = None      # Word count
    author: Optional[str] = None          # Document author
    title: Optional[str] = None           # Document title
    created_date: Optional[str] = None    # Creation date
    modified_date: Optional[str] = None   # Last modified date
    file_size: Optional[int] = None       # File size in bytes
    
    def to_dict(self) -> Dict[str, Any]:  # Convert to dict
        ...
```

**Example:**
```python
result = read_file("document.pdf")

# Access metadata
meta = result.metadata
print(f"Pages: {meta.page_count}")
print(f"Author: {meta.author}")
print(f"Size: {meta.file_size} bytes")

# Convert to dictionary
meta_dict = meta.to_dict()
# Returns: {'page_count': 10, 'author': 'John Doe', ...}
```

---

### Batch

Collection of files with optional category labels.

```python
@dataclass
class Batch:
    categories: List[str] = field(default_factory=list)  # Category labels
    files: List[BatchEntry] = field(default_factory=list)  # File entries
    
    def to_format(self) -> str:  # Convert to batch format string
        ...
```

**Example:**
```python
from docsearch import Batch, BatchEntry

# Create batch manually
batch = Batch(categories=["invoice", "2024"])
batch.files.append(BatchEntry(
    filepath="/docs/inv_001.pdf",
    filename="inv_001.pdf",
    extension=".pdf",
    size=12345,
    tokens="Invoice content here..."
))

# Convert to format string
output = batch.to_format()
```

---

### BatchEntry

Single file entry in a batch.

```python
@dataclass
class BatchEntry:
    filepath: str     # Full path to file
    filename: str     # Just filename
    extension: str    # File extension
    size: int         # File size in bytes
    tokens: str       # Extracted text tokens
    
    def to_format(self) -> str:  # Convert to batch format
        ...
```

---

### BatchCollection

Collection of multiple batches.

```python
@dataclass
class BatchCollection:
    batches: List[Batch] = field(default_factory=list)
    
    def to_format(self) -> str:  # Convert to batch format
        ...
    
    @classmethod
    def from_format(cls, text: str) -> 'BatchCollection':  # Parse from string
        ...
    
    def all_files(self) -> Iterator[tuple[List[str], BatchEntry]]:  # Iterate files
        ...
```

**Example:**
```python
from docsearch import BatchCollection

# Parse batch format
text = """<batch>
CATEGORIES: invoice
<file>
FILEPATH: /docs/inv_001.pdf
...
"""

collection = BatchCollection.from_format(text)

# Iterate over all files
for categories, entry in collection.all_files():
    print(f"{entry.filename}: {categories}")
```

---

## Batch Processing

### collect_files()

Recursively collect all files from a directory.

```python
from docsearch import collect_files

def collect_files(directory: str, recursive: bool = True) -> List[str]
```

**Parameters:**
- `directory` (str): Directory path to scan
- `recursive` (bool, optional): Process subdirectories. Default: True

**Returns:**
- `List[str]`: List of file paths

**Example:**
```python
from docsearch import collect_files

# Recursive collection (default)
all_files = collect_files("/documents")
print(f"Found {len(all_files)} files")

# Non-recursive (single directory only)
top_level = collect_files("/documents", recursive=False)
```

---

### create_batch_from_files()

Create a batch from a list of files.

```python
from docsearch import create_batch_from_files

def create_batch_from_files(
    files: List[str],
    categories: Optional[List[str]] = None,
    n_tokens: int = 250,
    show_progress: bool = False
) -> Batch
```

**Parameters:**
- `files` (List[str]): List of file paths
- `categories` (List[str], optional): Category labels
- `n_tokens` (int, optional): Tokens per file. Default: 250
- `show_progress` (bool, optional): Show progress bar. Default: False

**Returns:**
- `Batch`: Batch object with processed files

**Example:**
```python
from docsearch import create_batch_from_files

files = ["/docs/file1.pdf", "/docs/file2.pdf"]
batch = create_batch_from_files(
    files,
    categories=["invoice", "2024"],
    n_tokens=300,
    show_progress=True
)

print(f"Processed {len(batch.files)} files")
```

---

### create_labeled_batch_from_directory()

Quick function to create a labeled batch from a directory.

```python
from docsearch import create_labeled_batch_from_directory

def create_labeled_batch_from_directory(
    directory: str,
    categories: Optional[List[str]] = None,
    n_tokens: int = 250,
    recursive: bool = True,
    show_progress: bool = False
) -> str
```

**Parameters:**
- `directory` (str): Directory to process
- `categories` (List[str], optional): Category labels
- `n_tokens` (int, optional): Tokens per file. Default: 250
- `recursive` (bool, optional): Process subdirectories. Default: True
- `show_progress` (bool, optional): Show progress bar. Default: False

**Returns:**
- `str`: Batch format string ready to use

**Example:**
```python
from docsearch import create_labeled_batch_from_directory

# Create batch for classification
batch_text = create_labeled_batch_from_directory(
    "/documents/invoices",
    categories=["invoice", "financial"],
    n_tokens=250,
    recursive=True
)

# Save to file
with open("invoices_batch.md", "w") as f:
    f.write(batch_text)
```

---

### BatchBuilder

Builder pattern for complex multi-source batches.

```python
class BatchBuilder:
    def __init__(self):
        ...
    
    def add_directory(
        self,
        directory: str,
        categories: Optional[List[str]] = None,
        n_tokens: int = 250,
        recursive: bool = True
    ) -> 'BatchBuilder':
        ...
    
    def add_files(
        self,
        files: List[str],
        categories: Optional[List[str]] = None,
        n_tokens: int = 250
    ) -> 'BatchBuilder':
        ...
    
    def build(self) -> BatchCollection:
        ...
    
    def to_format(self) -> str:
        ...
```

**Example:**
```python
from docsearch import BatchBuilder

# Build complex batch from multiple sources
builder = BatchBuilder()

# Add invoices
builder.add_directory(
    "/accounting/invoices",
    categories=["invoice", "financial"]
)

# Add receipts
builder.add_directory(
    "/accounting/receipts",
    categories=["receipt", "financial"]
)

# Add specific contracts
builder.add_files(
    ["/contracts/contract1.pdf", "/contracts/contract2.pdf"],
    categories=["contract", "legal"]
)

# Build and output
batch_text = builder.to_format()

# Or get collection object
collection = builder.build()
print(f"Total batches: {len(collection.batches)}")
```

---

### files_from_text()

Parse file paths from text (one per line).

```python
from docsearch import files_from_text

def files_from_text(text: str) -> List[str]
```

**Example:**
```python
from docsearch import files_from_text

text = """
# My files
/docs/file1.pdf
/docs/file2.pdf
/docs/file3.pdf
"""

files = files_from_text(text)
# Returns: ['/docs/file1.pdf', '/docs/file2.pdf', '/docs/file3.pdf']
```

---

### files_from_file()

Read file paths from a text file.

```python
from docsearch import files_from_file

def files_from_file(filepath: str) -> List[str]
```

**Example:**
```python
from docsearch import files_from_file

# Read from file
files = files_from_file("file_list.txt")

# Process files
from docsearch import create_batch_from_files
batch = create_batch_from_files(files)
```

---

## Glob Pattern Filtering

### glob_matches()

Check if a filepath matches a glob pattern (case-sensitive).

```python
from docsearch import glob_matches

def glob_matches(filepath: str, pattern: str) -> bool
```

**Parameters:**
- `filepath` (str): Path to check
- `pattern` (str): Glob pattern (case-sensitive)

**Returns:**
- `bool`: True if filepath matches pattern

**Pattern Syntax:**
- `*` - Matches any characters except `/`
- `**` - Matches any characters including `/` (recursive)
- `?` - Matches single character
- `[seq]` - Matches any character in seq
- `[!seq]` - Matches any character not in seq

**Examples:**
```python
from docsearch import glob_matches

# Simple patterns
glob_matches("/docs/file.pdf", "*.pdf")          # True
glob_matches("/docs/file.PDF", "*.pdf")          # False (case-sensitive!)
glob_matches("/docs/invoice_001.pdf", "invoice_*")  # True

# Recursive patterns
glob_matches("/docs/2024/report.pdf", "2024/*.pdf")      # True
glob_matches("/docs/2024/Q1/report.pdf", "2024/**/*.pdf")  # True

# Character classes
glob_matches("/docs/file1.pdf", "file[0-9]*")    # True
glob_matches("/docs/fileA.pdf", "file[!0-9]*")   # True
```

---

### filter_files_by_glob()

Filter a list of files by glob pattern(s).

```python
from docsearch import filter_files_by_glob

def filter_files_by_glob(
    files: List[str],
    patterns: Optional[str]
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths
- `patterns` (str or None): Comma-separated glob patterns

**Returns:**
- `List[str]`: Filtered list of files

**Examples:**
```python
from docsearch import filter_files_by_glob

files = [
    "/docs/report.pdf",
    "/docs/data.xlsx",
    "/docs/README.md"
]

# Single pattern
pdfs = filter_files_by_glob(files, "*.pdf")
# Returns: ['/docs/report.pdf']

# Multiple patterns
docs = filter_files_by_glob(files, "*.pdf,*.xlsx")
# Returns: ['/docs/report.pdf', '/docs/data.xlsx']

# No filter
all_files = filter_files_by_glob(files, None)
# Returns: all files
```

---

### apply_glob_filter()

Filter files with optional verbose output.

```python
from docsearch import apply_glob_filter

def apply_glob_filter(
    files: List[str],
    glob_pattern: Optional[str],
    verbose: bool = False
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths
- `glob_pattern` (str or None): Glob pattern(s)
- `verbose` (bool, optional): Print statistics. Default: False

**Returns:**
- `List[str]`: Filtered list

**Example:**
```python
from docsearch import collect_files, apply_glob_filter

# Collect all files
all_files = collect_files("/documents")

# Filter with verbose output
pdfs = apply_glob_filter(all_files, "*.pdf", verbose=True)
# Prints: Glob filter '*.pdf': 42/156 files matched
```

---

## Metadata Search (Fast Filename/Path Search)

New in v2.1.0: Search filenames and paths without reading file contents.

### search_metadata()

Search for pattern in filenames/paths only (no file reading).

```python
from docsearch import search_metadata

def search_metadata(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> List[Tuple[str, Tuple[int, int]]]
```

**Parameters:**
- `files` (List[str]): List of file paths to search
- `pattern` (str or Pattern): Regex pattern (string or compiled)
- `case_sensitive` (bool, optional): Case-sensitive search. Default: True

**Returns:**
- `List[Tuple[str, Tuple[int, int]]]`: List of (filepath, (match_start, match_end))

**Performance:**
- 100x+ faster than content search (no file I/O)
- Works on locked/inaccessible files
- Ideal for finding files by naming patterns

**Examples:**
```python
from docsearch import search_metadata

files = [
    '/docs/invoice_2024_001.pdf',
    '/docs/invoice_2024_002.pdf',
    '/docs/receipt_2023.pdf',
    '/docs/contract.docx'
]

# Find files with "2024" in path
matches = search_metadata(files, '2024')
# Returns: [('/docs/invoice_2024_001.pdf', (14, 18)), 
#           ('/docs/invoice_2024_002.pdf', (14, 18))]

# Case-insensitive search
matches = search_metadata(files, 'INVOICE', case_sensitive=False)
# Returns: [('/docs/invoice_2024_001.pdf', (6, 13)), ...]

# Regex patterns
matches = search_metadata(files, r'_\d{4}_')
# Returns: [('/docs/invoice_2024_001.pdf', (13, 19)), ...]
```

---

### search_metadata_dict()

Search metadata and return results as a detailed dictionary.

```python
from docsearch import search_metadata_dict

def search_metadata_dict(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> dict
```

**Returns:**
Dictionary with:
- `matches` (List[str]): List of matched file paths
- `total_files` (int): Total number of files searched
- `matched_files` (int): Number of files matched
- `details` (List[dict]): List of dicts with filepath, match, start, end

**Example:**
```python
from docsearch import search_metadata_dict

result = search_metadata_dict(files, r'_\d{4}_')

print(f"Found {result['matched_files']} files")
# Output: Found 3 files

for detail in result['details']:
    print(f"{detail['filepath']}: '{detail['match']}' at pos {detail['start']}")
# Output:
#   /docs/invoice_2024_001.pdf: '_2024_' at pos 13
#   /docs/invoice_2024_002.pdf: '_2024_' at pos 13
#   /docs/receipt_2023.pdf: '_2023_' at pos 13
```

---

### filter_by_name_pattern()

Filter files by name pattern (convenience function).

```python
from docsearch import filter_by_name_pattern

def filter_by_name_pattern(
    files: List[str],
    pattern: Union[str, Pattern],
    case_sensitive: bool = True
) -> List[str]
```

**Returns:**
- `List[str]`: List of file paths that match the pattern

**Example:**
```python
from docsearch import filter_by_name_pattern

files = ['/docs/invoice_2024.pdf', '/docs/receipt.pdf', '/docs/contract.docx']

# Find all invoice files (case-insensitive)
invoices = filter_by_name_pattern(files, 'invoice', case_sensitive=False)
# Returns: ['/docs/invoice_2024.pdf']

# Find files with year pattern
year_2024 = filter_by_name_pattern(files, r'_2024')
# Returns: ['/docs/invoice_2024.pdf']
```

---

### highlight_match()

Highlight matched portion in filepath.

```python
from docsearch import highlight_match

def highlight_match(
    filepath: str,
    start: int,
    end: int,
    left_marker: str = '[',
    right_marker: str = ']'
) -> str
```

**Parameters:**
- `filepath` (str): Full file path
- `start` (int): Match start position
- `end` (int): Match end position
- `left_marker` (str, optional): Left marker. Default: '['
- `right_marker` (str, optional): Right marker. Default: ']'

**Returns:**
- `str`: String with match highlighted

**Example:**
```python
from docsearch import highlight_match

# Default markers [ ]
highlighted = highlight_match('/docs/invoice_2024.pdf', 13, 17)
print(highlighted)
# Output: /docs/invoice[_202]4.pdf

# Custom markers < >
highlighted = highlight_match('/docs/invoice_2024.pdf', 13, 17, '<', '>')
print(highlighted)
# Output: /docs/invoice<_202>4.pdf
```

---

## File Metadata Search (Dates, Size, PDF Metadata)

New in v2.2.0: Search and filter files by file system metadata and PDF document metadata.

### FileMetadataFilter

Dataclass for specifying filter criteria.

```python
from docsearch import FileMetadataFilter

@dataclass
class FileMetadataFilter:
    # Filename/path filters
    name_pattern: Optional[str] = None
    name_case_sensitive: bool = True
    
    # Date filters
    modified_after: Optional[Union[datetime, date, str]] = None
    modified_before: Optional[Union[datetime, date, str]] = None
    created_after: Optional[Union[datetime, date, str]] = None
    created_before: Optional[Union[datetime, date, str]] = None
    
    # Size filters (bytes)
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    
    # Extension filter
    extensions: Optional[List[str]] = None
    
    # PDF metadata filters
    pdf_author: Optional[str] = None
    pdf_title: Optional[str] = None
    pdf_keywords: Optional[str] = None
    pdf_case_sensitive: bool = False
```

**Example:**
```python
from docsearch import FileMetadataFilter, search_by_metadata

# Define criteria
criteria = FileMetadataFilter(
    extensions=['.pdf'],
    modified_after='2024-01-01',
    size_min=1_000_000,  # 1 MB
    pdf_author='John Doe'
)

# Search
matches = search_by_metadata(files, criteria)
```

---

### search_by_metadata()

Search files using FileMetadataFilter criteria.

```python
from docsearch import search_by_metadata, FileMetadataFilter

def search_by_metadata(
    files: List[str],
    filter_criteria: FileMetadataFilter
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths to search
- `filter_criteria` (FileMetadataFilter): Filter criteria

**Returns:**
- `List[str]`: List of matching file paths

**Example:**
```python
from docsearch import search_by_metadata, FileMetadataFilter

# Find large recent PDFs
criteria = FileMetadataFilter(
    extensions=['.pdf'],
    modified_after='2024-01-01',
    size_min=1_000_000
)

matches = search_by_metadata(files, criteria)
```

---

### filter_by_date()

Filter files by modification/creation dates (convenience function).

```python
from docsearch import filter_by_date

def filter_by_date(
    files: List[str],
    modified_after: Optional[Union[datetime, date, str]] = None,
    modified_before: Optional[Union[datetime, date, str]] = None,
    created_after: Optional[Union[datetime, date, str]] = None,
    created_before: Optional[Union[datetime, date, str]] = None
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths
- `modified_after`: Only files modified after this date
- `modified_before`: Only files modified before this date
- `created_after`: Only files created after this date
- `created_before`: Only files created before this date

**Date Formats Accepted:**
- ISO string: '2024-01-01' or '2024-01-01 09:00:00'
- datetime object
- date object

**Returns:**
- `List[str]`: List of matching file paths

**Examples:**
```python
from docsearch import filter_by_date
from datetime import datetime, timedelta

# Files modified in January 2024
matches = filter_by_date(
    files,
    modified_after='2024-01-01',
    modified_before='2024-01-31'
)

# Files created in the last week
week_ago = datetime.now() - timedelta(days=7)
recent = filter_by_date(files, created_after=week_ago)
```

---

### filter_by_size()

Filter files by size (convenience function).

```python
from docsearch import filter_by_size

def filter_by_size(
    files: List[str],
    min_bytes: Optional[int] = None,
    max_bytes: Optional[int] = None
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths
- `min_bytes` (int, optional): Minimum file size in bytes
- `max_bytes` (int, optional): Maximum file size in bytes

**Returns:**
- `List[str]`: List of matching file paths

**Examples:**
```python
from docsearch import filter_by_size

# Files larger than 1 MB
large = filter_by_size(files, min_bytes=1_000_000)

# Files between 100 KB and 10 MB
medium = filter_by_size(
    files,
    min_bytes=100_000,
    max_bytes=10_000_000
)
```

---

### filter_by_pdf_metadata()

Filter PDF files by metadata (convenience function).

Requires `pypdf` to be installed.

```python
from docsearch import filter_by_pdf_metadata

def filter_by_pdf_metadata(
    files: List[str],
    author: Optional[str] = None,
    title: Optional[str] = None,
    keywords: Optional[str] = None,
    case_sensitive: bool = False
) -> List[str]
```

**Parameters:**
- `files` (List[str]): List of file paths
- `author` (str, optional): Pattern to match in author field
- `title` (str, optional): Pattern to match in title field
- `keywords` (str, optional): Pattern to match in keywords field
- `case_sensitive` (bool): Case-sensitive matching (default: False)

**Returns:**
- `List[str]`: List of matching PDF file paths

**Examples:**
```python
from docsearch import filter_by_pdf_metadata

# PDFs by specific author
johns_docs = filter_by_pdf_metadata(files, author='John Doe')

# PDFs with "invoice" in title (case-insensitive)
invoices = filter_by_pdf_metadata(
    files,
    title='invoice',
    case_sensitive=False
)

# PDFs with specific keywords
reports = filter_by_pdf_metadata(files, keywords='quarterly')
```

---

### get_file_info()

Get comprehensive file information.

```python
from docsearch import get_file_info

def get_file_info(filepath: str) -> Dict[str, Any]
```

**Parameters:**
- `filepath` (str): Path to file

**Returns:**
- Dictionary with file information:
  - `filepath`: Full path
  - `filename`: Just filename
  - `extension`: File extension
  - `exists`: Whether file exists
  - `size`: File size in bytes
  - `modified`: Modification datetime
  - `created`: Creation datetime
  - `pdf_metadata`: PDF metadata dict (if PDF file)

**Example:**
```python
from docsearch import get_file_info

info = get_file_info('/docs/report.pdf')

print(f"File: {info['filename']}")
print(f"Size: {info['size']:,} bytes")
print(f"Modified: {info['modified']}")

if info['pdf_metadata']:
    print(f"Author: {info['pdf_metadata']['author']}")
    print(f"Title: {info['pdf_metadata']['title']}")
```

---

## CLI Commands

### extract

Extract tokens from files for classification.

```bash
docsearch extract [OPTIONS] PATH
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-g, --glob PATTERN` | Glob pattern to filter files | None |
| `-o, --output FILE` | Output file | stdout |
| `-a, --append` | Append to output file | False |
| `-c, --categories CATS` | Comma-separated categories | None |
| `-t, --tokens N` | Tokens per file | 250 |
| `-r, --recursive` | Process recursively | True |
| `--no-recursive` | Don't process subdirectories | - |
| `--file-list FILE` | Read paths from file | None |
| `-v, --verbose` | Show verbose progress | False |

**Examples:**
```bash
# Basic extraction
docsearch extract /documents -o batch.md

# Extract only PDFs
docsearch extract /documents --glob "*.pdf" -o pdfs.md

# With categories and verbose
docsearch extract /invoices --glob "*.pdf" \
    --categories "invoice,2024" -v -o batch.md

# From file list
docsearch extract --file-list paths.txt -o batch.md

# Append to existing batch
docsearch extract /new_docs --glob "*.pdf" -a -o batch.md
```

---

### search

Search files for regex patterns.

```bash
docsearch search [OPTIONS] PATH PATTERN
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-g, --glob PATTERN` | Glob pattern to filter files | None |
| `-i, --ignore-case` | Case-insensitive search | False |
| `-m, --metadata-only` | Search filenames only (no file reading) | False |
| `-r, --recursive` | Search recursively | True |
| `--no-recursive` | Don't search subdirectories | - |
| `-v, --verbose` | Show verbose output | False |

**Search Modes:**
- **Content Search** (default): Searches inside file contents
- **Metadata Search** (`--metadata-only`): Searches only filenames/paths (100x+ faster)

**Examples:**
```bash
# Basic search
docsearch search /documents "invoice"

# Search only in PDFs
docsearch search /documents "invoice" --glob "*.pdf"

# Case-insensitive regex
docsearch search /documents "INV-\d+" -i

# Search in specific directory pattern
docsearch search /documents "contract" --glob "**/2024/*.pdf"

# Verbose mode (shows files as searched)
docsearch search /documents "pattern" --glob "*.md" -v

# METADATA-ONLY SEARCH (NEW in v2.1.0)
# Search filenames only (fast - no file reading)
docsearch search /documents "2024" --metadata-only

# Find files with "invoice" in name
docsearch search /documents "invoice" --metadata-only -i

# Regex in filenames
docsearch search /documents "_\d{4}_" --metadata-only
```

**Metadata-Only Output:**
```
Matched files:
  /docs/invoice_[2024]_001.pdf
  /docs/invoice_[2024]_002.pdf

Total: 2 files matched (out of 140 searched)
```

**Understanding Output:**
```
Total: 26 matches in 15/140 files
```
- **26 matches** = Total pattern occurrences found across all files
- **15** = Number of files containing at least one match
- **140** = Total number of files searched

Only files with matches are displayed in the output. Use `-v` to see all files as they're being searched.

---

### info

Show file information and preview.

```bash
docsearch info [OPTIONS] FILE
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --tokens N` | Tokens to preview | 100 |

**Example:**
```bash
docsearch info document.pdf
docsearch info large_file.docx --tokens 50
```

---

### formats

List supported file formats.

```bash
docsearch formats
```

**Example:**
```bash
$ docsearch formats
Supported file formats:

  .pdf       PDFReader
  .docx      DocxReader
  .md        MarkdownReader
  .txt       MarkdownReader
```

---

## Error Handling

### Explicit Error States

DocSearch uses explicit error states instead of exceptions for better control flow:

```python
from docsearch import read_file, ReadStatus

result = read_file("document.pdf")

# Method 1: Check ok property
if result.ok:
    process(result.text)
else:
    print(f"Error: {result.error}")

# Method 2: Check specific status
if result.status == ReadStatus.SUCCESS:
    process(result.text)
elif result.status == ReadStatus.NOT_FOUND:
    print("File doesn't exist")
elif result.status == ReadStatus.CORRUPT_FILE:
    print("File is damaged")
else:
    print(f"Unexpected error: {result.error}")
```

### Error Status Reference

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| `SUCCESS` | File read successfully | - |
| `NOT_FOUND` | File doesn't exist | Wrong path, file deleted |
| `PERMISSION_DENIED` | No read permission | File permissions, admin required |
| `UNSUPPORTED_FORMAT` | File type not supported | Wrong extension, missing dependency |
| `CORRUPT_FILE` | File is damaged | Incomplete download, disk error |
| `EMPTY_FILE` | No content extracted | Empty file, no text in PDF |
| `READ_ERROR` | Other read error | Various issues |

---

## Advanced Usage

### Custom Readers

Add support for new file formats:

```python
from docsearch.readers import READER_REGISTRY, BaseReader
from docsearch.models import ReadResult, ReadStatus, FileMetadata
import os

class MyCustomReader:
    """Reader for .custom files."""
    
    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.endswith('.custom')
    
    @staticmethod
    def read(filepath: str) -> ReadResult:
        if not os.path.exists(filepath):
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.NOT_FOUND,
                error="File not found"
            )
        
        try:
            # Your custom reading logic
            with open(filepath, 'r') as f:
                text = f.read()
            
            metadata = FileMetadata(
                file_size=os.path.getsize(filepath),
                word_count=len(text.split())
            )
            
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.SUCCESS,
                text=text,
                metadata=metadata
            )
        except Exception as e:
            return ReadResult(
                filepath=filepath,
                status=ReadStatus.READ_ERROR,
                error=str(e)
            )

# Register your reader
READER_REGISTRY['.custom'] = MyCustomReader

# Now you can use it
from docsearch import read_file
result = read_file("file.custom")
```

### Parallel Processing

Process multiple files in parallel:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from docsearch import read_file_preview

def process_files_parallel(files, n_tokens=250, max_workers=4):
    """Process files in parallel."""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files
        future_to_file = {
            executor.submit(read_file_preview, f, n_tokens): f
            for f in files
        }
        
        # Collect results
        for future in as_completed(future_to_file):
            filepath = future_to_file[future]
            try:
                result = future.result()
                results[filepath] = result
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    return results

# Usage
files = ["/docs/file1.pdf", "/docs/file2.pdf", "/docs/file3.pdf"]
results = process_files_parallel(files, max_workers=4)

for filepath, result in results.items():
    if result.ok:
        print(f"✓ {filepath}")
    else:
        print(f"✗ {filepath}: {result.error}")
```

### Streaming Large Batches

Process large batches without loading all into memory:

```python
from docsearch import BatchCollection

def process_batch_streaming(batch_file):
    """Process batch entries one at a time."""
    
    with open(batch_file, 'r') as f:
        text = f.read()
    
    collection = BatchCollection.from_format(text)
    
    # Process files one at a time
    for categories, entry in collection.all_files():
        # Process this entry
        print(f"Processing {entry.filename} ({categories})")
        
        # Your processing logic here
        analyze(entry.tokens, categories)
        
        # Entry goes out of scope, memory can be freed
```

### Complex Filtering

Combine glob patterns with custom logic:

```python
from docsearch import collect_files, filter_files_by_glob
import os
from datetime import datetime, timedelta

def get_recent_pdfs(directory, days=7):
    """Get PDFs modified in last N days."""
    
    # Collect and filter by extension
    all_files = collect_files(directory)
    pdfs = filter_files_by_glob(all_files, "*.pdf")
    
    # Filter by modification time
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    
    for filepath in pdfs:
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime > cutoff:
            recent.append(filepath)
    
    return recent

# Usage
recent_pdfs = get_recent_pdfs("/documents", days=7)
print(f"Found {len(recent_pdfs)} recent PDFs")
```

---

## Complete Example

Putting it all together - a complete classification workflow:

```python
from docsearch import (
    BatchBuilder,
    filter_files_by_glob,
    collect_files,
    BatchCollection
)

# Step 1: Build batch from multiple sources
builder = BatchBuilder()

# Add invoices (only PDFs from 2024)
invoice_files = collect_files("/accounting/invoices")
invoice_pdfs = filter_files_by_glob(invoice_files, "**/2024/*.pdf")
builder.add_files(invoice_pdfs, categories=["invoice", "2024"])

# Add receipts
builder.add_directory(
    "/accounting/receipts",
    categories=["receipt", "2024"]
)

# Add contracts
builder.add_directory(
    "/legal/contracts",
    categories=["contract", "legal"]
)

# Step 2: Generate batch file
batch_text = builder.to_format()

with open("classification_batch.md", "w") as f:
    f.write(batch_text)

print("Batch file created: classification_batch.md")

# Step 3: Later, parse and process
with open("classification_batch.md", "r") as f:
    loaded_text = f.read()

collection = BatchCollection.from_format(loaded_text)

# Step 4: Process each file
for categories, entry in collection.all_files():
    print(f"File: {entry.filename}")
    print(f"Categories: {', '.join(categories)}")
    print(f"Preview: {entry.tokens[:100]}...")
    print()
    
    # Your classification logic here
    # classify_document(entry.tokens, categories)
```

---

## Version History

**v2.1.0** (Current)
- Added metadata-only search (--metadata-only flag)
- Added Python API for filename/path searching (4 new functions)
- 100x+ faster than content search for finding files by name

**v2.0.2**
- Improved search output clarity (shows files with matches / total searched)
- Added verbose mode to show files as they're being searched

**v2.0.1**
- Fixed case-sensitive glob matching on all platforms
- Fixed batch parsing with multiple files
- Comprehensive documentation

**v2.0.0**
- Added glob pattern filtering
- Enhanced CLI with --glob parameter
- Improved error handling

**v1.0.0**
- Initial release
- Multi-format support
- Batch processing
- CLI interface

---

## Support

For issues, questions, or feature requests, please refer to:
- README.md for general usage
- CHEATSHEET.md for quick reference
- BUGFIXES.md for known issues

---

*Last updated: February 16, 2026 - v2.1.0*
