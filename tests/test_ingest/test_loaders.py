"""
Tests for document loaders.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from ingest.loaders.pdf import load_pdf
from ingest.loaders import load_document, get_loader


class TestPDFLoader:
    """Tests for PDF loader."""
    
    @patch('ingest.loaders.pdf.PdfReader')
    def test_load_pdf(self, mock_pdf_reader):
        """Test PDF loading."""
        # Setup mock
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        # Test
        result = load_pdf("test.pdf")
        
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        mock_pdf_reader.assert_called_once_with("test.pdf")


class TestLoaderFactory:
    """Tests for loader factory."""
    
    def test_get_loader_pdf(self):
        """Test get loader for PDF."""
        file_type = get_loader("document.pdf")
        assert file_type == "pdf"
    
    def test_get_loader_txt(self):
        """Test get loader for TXT."""
        file_type = get_loader("document.txt")
        assert file_type == "txt"
    
    def test_get_loader_docx(self):
        """Test get loader for DOCX."""
        file_type = get_loader("document.docx")
        assert file_type == "docx"
    
    def test_get_loader_unsupported(self):
        """Test get loader for unsupported type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_loader("document.xyz")
    
    @patch('ingest.loaders.pdf.PdfReader')
    def test_load_document_pdf(self, mock_pdf_reader):
        """Test load document with PDF."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        result = load_document("test.pdf")
        
        assert "Test content" in result
    
    @patch('builtins.open', new_callable=mock_open, read_data="Test TXT content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_document_txt(self, mock_exists, mock_file):
        """Test load document with TXT."""
        result = load_document("test.txt")
        
        assert "Test TXT content" in result
    
    def test_load_document_docx_not_implemented(self):
        """Test load document with DOCX raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            load_document("test.docx")

