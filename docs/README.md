# DocSearch v2.1.0

> A Python toolkit for document search and classification workflows with glob pattern filtering

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Stable](https://img.shields.io/badge/status-stable-green.svg)]()

## Quick Start

```bash
# Install
pip install docsearch[full]

# Python API
from docsearch import read_file
result = read_file("document.pdf")
if result.ok:
    print(result.text)

# CLI
docsearch extract /documents --glob "*.pdf" -o batch.md

# NEW: Fast filename search (no file reading)
docsearch search /documents "2024" --metadata-only
```

## Documentation

📚 **[API.md](API.md)** - Complete API reference (40 pages)  
⚡ **[CHEATSHEET.md](CHEATSHEET.md)** - Quick reference guide  
📖 **[INSTALL.md](INSTALL.md)** - Installation & usage guide  
📝 **[CHANGELOG.md](CHANGELOG.md)** - Version history  
🐛 **[BUGFIXES.md](BUGFIXES.md)** - Known issues & fixes  

## Features

✓ Multi-format support (PDF, DOCX, Markdown, Text)  
✓ Glob pattern filtering (case-sensitive)  
✓ **NEW: Metadata-only search (100x+ faster)**  
✓ Rich metadata extraction  
✓ Batch processing for classification  
✓ Explicit error handling  
✓ CLI & Python API  

## Installation

```bash
pip install docsearch[full]
```

See [INSTALL.md](INSTALL.md) for detailed installation options.

## Quick Examples

### Python

```python
# Read file
from docsearch import read_file
result = read_file("doc.pdf")

# Glob matching
from docsearch import glob_matches
if glob_matches("/docs/file.pdf", "*.pdf"):
    print("Match!")

# Create batch
from docsearch import create_labeled_batch_from_directory
batch = create_labeled_batch_from_directory(
    "/invoices",
    categories=["invoice"]
)

# NEW: Fast filename search
from docsearch import search_metadata
matches = search_metadata(files, '2024')
```

### CLI

```bash
# Extract PDFs
docsearch extract /docs --glob "*.pdf" -o batch.md

# Search in Word docs
docsearch search /docs "pattern" --glob "*.docx"

# NEW: Search filenames only (fast)
docsearch search /docs "2024" --metadata-only

# File info
docsearch info document.pdf
```

## Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** (this file) | Quick start & overview |
| **[API.md](API.md)** | Complete API documentation |
| **[CHEATSHEET.md](CHEATSHEET.md)** | Quick reference for common tasks |
| **[INSTALL.md](INSTALL.md)** | Installation & setup guide |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history & changes |
| **[BUGFIXES.md](BUGFIXES.md)** | Bug fixes in v2.0.1 |
| **COMPLETE_SOURCE_CODE.md** | All source code in one file |
| **verify_fixes.py** | Test script to verify installation |

## What's New in v2.1.0

- 🚀 **New Feature**: Metadata-only search (`--metadata-only` flag)
  - 100x+ faster than content search
  - Works on locked/protected files
  - Search filenames without reading files
- 📦 **New Python API**: 4 new functions for filename searching
  - `search_metadata()`
  - `search_metadata_dict()`
  - `filter_by_name_pattern()`
  - `highlight_match()`
- 📊 **Improved**: Search output clarity (v2.0.2)
- 🐛 **Fixed**: Case-sensitive glob matching (v2.0.1)
- ✅ **All tests passing** (10/10)

## Support

- **Questions?** See [API.md](API.md) for detailed documentation
- **Quick Reference?** See [CHEATSHEET.md](CHEATSHEET.md)
- **Issues?** Check [BUGFIXES.md](BUGFIXES.md)

## License

MIT License

---

**Version:** 2.1.0 | **Status:** Stable | **Tests:** 10/10 ✓

*For complete documentation, start with [API.md](API.md) or [CHEATSHEET.md](CHEATSHEET.md)*
