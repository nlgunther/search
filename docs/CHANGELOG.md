# Changelog

All notable changes to the docsearch project will be documented in this file.

## [2.1.0] - 2026-02-16

### Added

- **Metadata-only search**: New `--metadata-only` (`-m`) flag for searching filenames/paths without reading files
- **Python API for metadata search**: Four new functions exported from `docsearch.metadata_search`
  - `search_metadata()` - Search filenames with position info
  - `search_metadata_dict()` - Search with detailed statistics
  - `filter_by_name_pattern()` - Simple filename filtering
  - `highlight_match()` - Highlight matched portion in paths

### Benefits

- **Speed**: 100x+ faster than content search for large directories
- **No file access**: Works on locked/protected files
- **Highlighted output**: Shows exactly what matched in the filename

### Examples

```bash
# CLI - Search filenames only
docsearch search /docs "2024" --metadata-only

# Python API
from docsearch import search_metadata, filter_by_name_pattern

matches = search_metadata(files, '2024')
invoices = filter_by_name_pattern(files, 'invoice', case_sensitive=False)
```

## [2.0.2] - 2026-02-16

### Improved

- **Search output clarity**: Summary now shows "X matches in Y/Z files" where Y = files with matches, Z = total files searched
- **Verbose search**: Added `-v` flag to show which files are being searched in real-time

### Example

```bash
# Before (confusing):
Total: 26 matches in 140 files

# After (clear):
Total: 26 matches in 15/140 files
# Means: 26 total occurrences found in 15 files (out of 140 searched)
```

## [2.0.1] - 2026-02-16

### Fixed

- **Case-sensitive matching**: Fixed `fnmatch` to use `fnmatchcase` for consistent case-sensitive behavior across all platforms (Windows, Linux, macOS)
- **Batch parsing**: Fixed `AttributeError` when parsing batches with multiple files
- **Tests**: Updated test suite to verify case-sensitive behavior

### Technical Details

**Issue:** On Windows, `fnmatch.fnmatch()` is case-insensitive, causing `*.pdf` to match `file.PDF`.

**Solution:** Use `fnmatch.fnmatchcase()` for filename patterns, which is case-sensitive on all platforms.

**Impact:** Glob patterns now behave consistently across platforms. `*.pdf` matches `file.pdf` but NOT `file.PDF`.

## [2.0.0] - 2026-02-16

### Added - Glob Pattern Filtering

- **Glob pattern filtering**: New `--glob` / `-g` parameter for `extract` and `search` commands
- **glob_filter module**: Complete glob pattern matching implementation
  - `glob_matches()`: Check if filepath matches glob pattern
  - `filter_files_by_glob()`: Filter file lists by pattern(s)
  - `apply_glob_filter()`: Filter with optional verbose output
- **Pattern support**:
  - `*` - Matches any characters except `/`
  - `**` - Matches any characters including `/` (recursive)
  - `?` - Single character matching
  - `[seq]` - Character class matching
  - `[!seq]` - Negated character class
  - Comma-separated multiple patterns
- **CLI integration**: Seamless integration into existing commands
- **Comprehensive documentation**: Glob pattern guide with examples
- **Tests**: Full test coverage for glob matching

### Enhanced

- **CLI**: Updated `extract` and `search` commands with glob filtering
- **API**: Public API now exports glob filter functions
- **Documentation**: Extensive README with glob pattern examples
- **Error handling**: Better error messages for glob filtering

### Fixed

- **Optional dependencies**: Made tqdm import optional (no crash if not installed)

### Technical Details

**Files Modified:**
- `docsearch/cli.py` - Added glob parameter and filtering logic
- `docsearch/__init__.py` - Export glob filter functions
- `docsearch/batch.py` - Made tqdm optional

**Files Added:**
- `docsearch/glob_filter.py` - Core glob pattern implementation

**Migration Guide:**

No breaking changes. All existing code continues to work.

New features are opt-in via the `--glob` parameter:

```bash
# Old way (still works)
docsearch extract /documents -o batch.md

# New way (with filtering)
docsearch extract /documents --glob "*.pdf" -o batch.md
```

Python API additions:

```python
# New in v2.0
from docsearch import glob_matches, filter_files_by_glob, apply_glob_filter

# All v1.0 APIs still work
from docsearch import read_file, create_labeled_batch_from_directory
```

## [1.0.0] - 2026-01-15

### Initial Release

- Multi-format document reading (PDF, DOCX, Markdown, TXT)
- Rich metadata extraction
- Batch processing for classification workflows
- Explicit error handling with ReadStatus enum
- CLI interface (extract, search, info, formats commands)
- Extensible reader registry
- Comprehensive test suite
- Full documentation

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Upgrade Instructions

### From 1.0 to 2.0

**No action required** - v2.0 is fully backward compatible.

To use new glob features:

```bash
# Install/upgrade
pip install --upgrade docsearch

# Use new glob parameter
docsearch extract /docs --glob "*.pdf" -o batch.md
```

In Python:

```python
# Import new glob functions
from docsearch import filter_files_by_glob

files = ["/docs/a.pdf", "/docs/b.docx"]
pdfs = filter_files_by_glob(files, "*.pdf")
```

## Future Plans

### v2.1 (Planned)

- Additional file format readers (Excel, ODT, RTF)
- Parallel processing for large file sets
- Enhanced progress reporting
- Pattern validation and suggestions

### v2.2 (Planned)

- Negative glob patterns (exclude files)
- Case-insensitive glob mode
- Saved pattern presets
- Pattern statistics

### v3.0 (Future)

- Machine learning keyword extraction
- Confidence-based classification
- LLM integration
- Advanced batch workflows
