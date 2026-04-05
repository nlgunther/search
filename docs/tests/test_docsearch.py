"""
Basic tests for docsearch package.

Run with: pytest tests/
"""

import pytest
from docsearch import (
    read_file,
    read_file_preview,
    ReadStatus,
    glob_matches,
    filter_files_by_glob,
    BatchCollection,
)


class TestGlobMatching:
    """Test glob pattern matching."""
    
    def test_simple_patterns(self):
        """Test simple filename patterns."""
        assert glob_matches("/docs/file.pdf", "*.pdf")
        assert not glob_matches("/docs/file.pdf", "*.docx")
        assert glob_matches("/docs/invoice_001.pdf", "invoice_*.pdf")
    
    def test_recursive_patterns(self):
        """Test recursive directory patterns."""
        assert glob_matches("/docs/subdir/file.pdf", "**/*.pdf")
        assert glob_matches("/docs/2024/Q1/inv.pdf", "2024/**/*.pdf")
        assert glob_matches("/docs/invoices/inv.pdf", "**/invoices/*.pdf")
    
    def test_character_classes(self):
        """Test character class patterns."""
        assert glob_matches("/docs/report_A.pdf", "report_[A-Z]*")
        assert glob_matches("/docs/file1.pdf", "file[0-9]*")
    
    def test_case_sensitivity(self):
        """Test case-sensitive matching."""
        # Pattern matching is case-sensitive
        assert glob_matches("/docs/file.pdf", "*.pdf")
        # Note: On Windows, filesystem may be case-insensitive,
        # but pattern matching itself is case-sensitive
        # This test verifies the pattern matcher behavior
        assert glob_matches("/docs/file.PDF", "*.PDF")
        assert not glob_matches("/docs/file.pdf", "*.PDF")


class TestFileFiltering:
    """Test file filtering."""
    
    def test_single_pattern(self):
        """Test filtering with single pattern."""
        files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
        result = filter_files_by_glob(files, "*.pdf")
        assert result == ["/docs/a.pdf"]
    
    def test_multiple_patterns(self):
        """Test filtering with multiple patterns."""
        files = ["/docs/a.pdf", "/docs/b.docx", "/docs/c.txt"]
        result = filter_files_by_glob(files, "*.pdf,*.docx")
        assert len(result) == 2
        assert "/docs/a.pdf" in result
        assert "/docs/b.docx" in result
    
    def test_no_pattern(self):
        """Test filtering with no pattern."""
        files = ["/docs/a.pdf", "/docs/b.docx"]
        result = filter_files_by_glob(files, None)
        assert result == files


class TestBatchFormat:
    """Test batch format parsing."""
    
    def test_parse_simple_batch(self):
        """Test parsing simple batch."""
        text = """<batch>
CATEGORIES: test
<file>
FILEPATH: /test.pdf
FILENAME: test.pdf
EXTENSION: .pdf
SIZE: 1234
TOKENS:
Test content here
"""
        collection = BatchCollection.from_format(text)
        assert len(collection.batches) == 1
        assert collection.batches[0].categories == ["test"]
        assert len(collection.batches[0].files) == 1
        assert collection.batches[0].files[0].filename == "test.pdf"
    
    def test_parse_multiple_files(self):
        """Test parsing multiple files."""
        text = """<batch>
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
"""
        collection = BatchCollection.from_format(text)
        assert len(collection.batches[0].files) == 2


class TestReadResult:
    """Test ReadResult functionality."""
    
    def test_ok_property(self):
        """Test ok property."""
        from docsearch.models import ReadResult, ReadStatus
        
        result = ReadResult(
            filepath="/test.pdf",
            status=ReadStatus.SUCCESS
        )
        assert result.ok
        
        result = ReadResult(
            filepath="/test.pdf",
            status=ReadStatus.NOT_FOUND
        )
        assert not result.ok


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
