"""
Basic tests for docsearch package.

Run with: python tests/test_docsearch.py
or with pytest: pytest tests/
"""

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

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
        """Test case-sensitive matching (platform-specific)."""
        import platform
        
        # Pattern matching is case-sensitive on Unix/Linux
        # Pattern matching is case-insensitive on Windows
        assert glob_matches("/docs/file.pdf", "*.pdf")
        
        is_windows = platform.system() == 'Windows'
        
        if is_windows:
            # On Windows: case-insensitive (*.pdf matches *.PDF)
            assert glob_matches("/docs/file.PDF", "*.pdf")
            assert glob_matches("/docs/file.pdf", "*.PDF")
        else:
            # On Unix/Linux: case-sensitive (*.pdf does NOT match *.PDF)
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


class TestMetadataSearch:
    """Test metadata-only search feature (v2.1.0)."""
    
    def test_search_metadata_basic(self):
        """Test basic metadata search."""
        from docsearch import search_metadata
        
        files = ['/docs/invoice_2024.pdf', '/docs/report.pdf']
        matches = search_metadata(files, '2024')
        
        assert len(matches) == 1
        assert matches[0][0] == '/docs/invoice_2024.pdf'
        assert matches[0][1] == (14, 18)  # position
    
    def test_search_metadata_case_insensitive(self):
        """Test case-insensitive metadata search."""
        from docsearch import search_metadata
        
        files = ['/docs/Invoice_2024.pdf', '/docs/report.pdf']
        
        # Case-sensitive (default)
        matches_case = search_metadata(files, 'invoice', case_sensitive=True)
        assert len(matches_case) == 0
        
        # Case-insensitive
        matches_nocase = search_metadata(files, 'invoice', case_sensitive=False)
        assert len(matches_nocase) == 1
    
    def test_search_metadata_regex(self):
        """Test regex patterns in metadata search."""
        from docsearch import search_metadata
        
        files = [
            '/docs/invoice_2024_001.pdf',
            '/docs/invoice_2024_002.pdf',
            '/docs/receipt_2023.pdf'
        ]
        
        # Regex: underscore followed by 4 digits
        matches = search_metadata(files, r'_\d{4}_')
        assert len(matches) == 2  # Two invoices match
    
    def test_filter_by_name_pattern(self):
        """Test simple filename filtering."""
        from docsearch import filter_by_name_pattern
        
        files = [
            '/docs/invoice.pdf',
            '/docs/receipt.pdf',
            '/docs/Invoice_2024.pdf'
        ]
        
        # Case-sensitive
        matches = filter_by_name_pattern(files, 'invoice', case_sensitive=True)
        assert len(matches) == 1
        assert matches[0] == '/docs/invoice.pdf'
        
        # Case-insensitive
        matches_nocase = filter_by_name_pattern(files, 'invoice', case_sensitive=False)
        assert len(matches_nocase) == 2
    
    def test_search_metadata_dict(self):
        """Test metadata search with detailed results."""
        from docsearch import search_metadata_dict
        
        files = ['/docs/invoice_2024.pdf', '/docs/report.pdf']
        result = search_metadata_dict(files, '2024')
        
        assert result['total_files'] == 2
        assert result['matched_files'] == 1
        assert len(result['matches']) == 1
        assert len(result['details']) == 1
        assert result['details'][0]['match'] == '2024'
    
    def test_highlight_match(self):
        """Test match highlighting."""
        from docsearch import highlight_match
        
        # Default markers
        result = highlight_match('/docs/invoice_2024.pdf', 14, 18)
        assert '[' in result
        assert ']' in result
        assert '2024' in result
        
        # Custom markers
        result = highlight_match('/docs/invoice_2024.pdf', 14, 18, '<', '>')
        assert '<' in result
        assert '>' in result
        assert '2024' in result
    
    def test_no_matches(self):
        """Test when no files match."""
        from docsearch import search_metadata, filter_by_name_pattern
        
        files = ['/docs/report.pdf', '/docs/notes.txt']
        
        matches = search_metadata(files, 'invoice')
        assert len(matches) == 0
        
        filtered = filter_by_name_pattern(files, 'invoice')
        assert len(filtered) == 0


class TestFileMetadataSearch:
    """Test file metadata search (v2.2.0)."""
    
    def test_filter_by_date(self):
        """Test date filtering."""
        from docsearch import filter_by_date
        from datetime import datetime, timedelta
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Should match (created today)
            yesterday = datetime.now() - timedelta(days=1)
            matches = filter_by_date([test_file], modified_after=yesterday)
            assert len(matches) == 1
            
            # Should not match (modified before yesterday)
            matches = filter_by_date([test_file], modified_before=yesterday)
            assert len(matches) == 0
    
    def test_filter_by_size(self):
        """Test size filtering."""
        from docsearch import filter_by_size
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files of different sizes
            small = os.path.join(tmpdir, 'small.txt')
            large = os.path.join(tmpdir, 'large.txt')
            
            with open(small, 'w') as f:
                f.write('x' * 100)
            with open(large, 'w') as f:
                f.write('x' * 10000)
            
            files = [small, large]
            
            # Filter by minimum size
            big_files = filter_by_size(files, min_bytes=1000)
            assert len(big_files) == 1
            assert 'large.txt' in big_files[0]
            
            # Filter by maximum size
            small_files = filter_by_size(files, max_bytes=500)
            assert len(small_files) == 1
            assert 'small.txt' in small_files[0]
    
    def test_get_file_info(self):
        """Test get_file_info."""
        from docsearch import get_file_info
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            info = get_file_info(test_file)
            assert info['exists']
            assert info['size'] > 0
            assert info['filename'] == 'test.txt'
            assert info['extension'] == '.txt'
            assert info['modified'] is not None
            assert info['created'] is not None
    
    def test_combined_filters(self):
        """Test FileMetadataFilter with multiple criteria."""
        from docsearch import FileMetadataFilter, search_by_metadata
        from datetime import datetime, timedelta
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('x' * 5000)
            
            yesterday = datetime.now() - timedelta(days=1)
            
            # Should match (size > 1000 AND modified after yesterday)
            criteria = FileMetadataFilter(
                size_min=1000,
                modified_after=yesterday
            )
            matches = search_by_metadata([test_file], criteria)
            assert len(matches) == 1
            
            # Should not match (size > 100000)
            criteria = FileMetadataFilter(
                size_min=100000
            )
            matches = search_by_metadata([test_file], criteria)
            assert len(matches) == 0
    
    def test_date_string_formats(self):
        """Test different date input formats."""
        from docsearch import filter_by_date
        from datetime import datetime, date, timedelta
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # ISO string format
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            matches = filter_by_date([test_file], modified_after=yesterday_str)
            assert len(matches) == 1
            
            # datetime object
            yesterday_dt = datetime.now() - timedelta(days=1)
            matches = filter_by_date([test_file], modified_after=yesterday_dt)
            assert len(matches) == 1
            
            # date object
            yesterday_date = date.today() - timedelta(days=1)
            matches = filter_by_date([test_file], modified_after=yesterday_date)
            assert len(matches) == 1
    
    def test_extension_filter(self):
        """Test extension filtering in FileMetadataFilter."""
        from docsearch import FileMetadataFilter, search_by_metadata
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = os.path.join(tmpdir, 'doc.pdf')
            txt_file = os.path.join(tmpdir, 'doc.txt')
            
            with open(pdf_file, 'w') as f:
                f.write('pdf')
            with open(txt_file, 'w') as f:
                f.write('txt')
            
            files = [pdf_file, txt_file]
            
            # Filter for PDFs only
            criteria = FileMetadataFilter(extensions=['.pdf'])
            matches = search_by_metadata(files, criteria)
            assert len(matches) == 1
            assert matches[0].endswith('.pdf')


class TestSearchOutput:
    """Test search command with --output flag."""
    
    def test_search_with_output_file(self):
        """Test search command writes to output file."""
        import tempfile
        import os
        import sys
        from io import StringIO
        
        # Add parent directory to path for CLI import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = os.path.join(tmpdir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('This contains the word invoice in the text.')
            
            output_file = os.path.join(tmpdir, 'results.txt')
            
            # Simulate command-line arguments
            class Args:
                path = tmpdir
                pattern = 'invoice'
                glob = None
                ignore_case = False
                metadata_only = False
                output = output_file
                recursive = True
                verbose = False
                modified_after = None
                modified_before = None
                created_after = None
                created_before = None
                size_min = None
                size_max = None
                extension = None
                pdf_author = None
                pdf_title = None
            
            args = Args()
            
            # Import and run command
            from docsearch.cli import cmd_search
            
            # Capture stderr
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            
            try:
                result = cmd_search(args)
                stderr_output = sys.stderr.getvalue()
                
                # Check command succeeded
                assert result == 0
                
                # Check output file was created
                assert os.path.exists(output_file)
                
                # Check output file contains match
                with open(output_file, 'r') as f:
                    content = f.read()
                    assert 'invoice' in content.lower()
                    assert test_file in content
                
                # Check stderr contains summary
                assert 'Total:' in stderr_output
                assert 'Results written to:' in stderr_output
                
            finally:
                sys.stderr = old_stderr
    
    def test_search_metadata_with_output(self):
        """Test metadata search with output file."""
        import tempfile
        import os
        import sys
        from io import StringIO
        
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file1 = os.path.join(tmpdir, 'invoice_2024.txt')
            test_file2 = os.path.join(tmpdir, 'report.txt')
            
            with open(test_file1, 'w') as f:
                f.write('test')
            with open(test_file2, 'w') as f:
                f.write('test')
            
            output_file = os.path.join(tmpdir, 'results.txt')
            
            class Args:
                path = tmpdir
                pattern = '2024'
                glob = None
                ignore_case = False
                metadata_only = True
                output = output_file
                recursive = True
                verbose = False
                modified_after = None
                modified_before = None
                created_after = None
                created_before = None
                size_min = None
                size_max = None
                extension = None
                pdf_author = None
                pdf_title = None
            
            args = Args()
            
            from docsearch.cli import cmd_search
            
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            
            try:
                result = cmd_search(args)
                
                assert result == 0
                assert os.path.exists(output_file)
                
                with open(output_file, 'r') as f:
                    content = f.read()
                    # Check for pattern match (may have highlight brackets)
                    assert '2024' in content
                    assert 'invoice' in content
                    assert 'Matched files' in content
                    
            finally:
                sys.stderr = old_stderr


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        # Run tests without pytest
        import sys
        
        test_classes = [
            TestGlobMatching,
            TestFileFiltering,
            TestBatchFormat,
            TestReadResult,
            TestMetadataSearch,
            TestFileMetadataSearch,
            TestSearchOutput
        ]
        
        total_tests = 0
        passed_tests = 0
        
        print("Running docsearch tests...\n")
        
        for test_class in test_classes:
            print(f'{test_class.__name__}:')
            test_obj = test_class()
            
            # Get all test methods
            test_methods = [m for m in dir(test_obj) if m.startswith('test_')]
            
            for method_name in test_methods:
                total_tests += 1
                try:
                    method = getattr(test_obj, method_name)
                    method()
                    print(f'  ✓ {method_name}')
                    passed_tests += 1
                except Exception as e:
                    print(f'  ✗ {method_name}: {str(e)[:60]}')
        
        print(f'\n{"="*60}')
        print(f'{passed_tests}/{total_tests} tests passed')
        if passed_tests == total_tests:
            print('✓ All tests PASSED')
            sys.exit(0)
        else:
            print(f'✗ {total_tests - passed_tests} tests FAILED')
            sys.exit(1)

