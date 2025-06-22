"""
Tests for RAG processors functionality.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from rag.processors.document_processor import DocumentProcessor
from rag.processors.vector_store import VectorStore


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    def test_processor_initialization(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        assert processor is not None
    
    def test_process_text_document(self):
        """Test processing a text document."""
        processor = DocumentProcessor()
        text_content = "This is a test document about hazardous substances."
        
        result = processor.process_text(text_content)
        assert result is not None
        assert "content" in result
        assert "metadata" in result
        assert result["content"] == text_content
    
    def test_process_pdf_document(self, temp_data_dir):
        """Test processing a PDF document."""
        processor = DocumentProcessor()
        
        # Create a mock PDF file
        pdf_file = os.path.join(temp_data_dir, "test.pdf")
        with open(pdf_file, 'w') as f:
            f.write("Mock PDF content")
        
        with patch('rag.processors.document_processor.PyPDF2') as mock_pdf:
            mock_reader = Mock()
            mock_reader.pages = [Mock(extract_text=lambda: "PDF content")]
            mock_pdf.PdfReader.return_value = mock_reader
            
            result = processor.process_pdf(pdf_file)
            assert result is not None
            assert "content" in result
            assert "metadata" in result
    
    def test_process_word_document(self, temp_data_dir):
        """Test processing a Word document."""
        processor = DocumentProcessor()
        
        # Create a mock Word file
        docx_file = os.path.join(temp_data_dir, "test.docx")
        with open(docx_file, 'w') as f:
            f.write("Mock Word content")
        
        with patch('rag.processors.document_processor.Document') as mock_doc:
            mock_doc.return_value.paragraphs = [Mock(text="Word content")]
            
            result = processor.process_word(docx_file)
            assert result is not None
            assert "content" in result
            assert "metadata" in result
    
    def test_chunk_document(self):
        """Test chunking a document into smaller pieces."""
        processor = DocumentProcessor()
        document = {
            "content": "This is a long document that needs to be chunked into smaller pieces for processing.",
            "metadata": {"source": "test.txt"}
        }
        
        chunks = processor.chunk_document(document, chunk_size=20, overlap=5)
        assert len(chunks) > 1
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_extract_metadata(self):
        """Test extracting metadata from document."""
        processor = DocumentProcessor()
        document_path = "/path/to/document.pdf"
        
        metadata = processor.extract_metadata(document_path)
        assert metadata is not None
        assert "filename" in metadata
        assert "file_extension" in metadata
        assert metadata["filename"] == "document.pdf"
        assert metadata["file_extension"] == "pdf"
    
    def test_validate_document(self):
        """Test document validation."""
        processor = DocumentProcessor()
        
        # Valid document
        valid_doc = {
            "content": "Valid content",
            "metadata": {"source": "test.txt"}
        }
        result = processor.validate_document(valid_doc)
        assert result["valid"] is True
        
        # Invalid document
        invalid_doc = {
            "content": "",
            "metadata": {}
        }
        result = processor.validate_document(invalid_doc)
        assert result["valid"] is False
    
    def test_process_multiple_documents(self):
        """Test processing multiple documents."""
        processor = DocumentProcessor()
        documents = [
            {"content": "Document 1", "metadata": {"source": "doc1.txt"}},
            {"content": "Document 2", "metadata": {"source": "doc2.txt"}},
            {"content": "Document 3", "metadata": {"source": "doc3.txt"}}
        ]
        
        results = processor.process_multiple_documents(documents)
        assert len(results) == 3
        assert all("content" in doc for doc in results)
        assert all("metadata" in doc for doc in results)


class TestVectorStore:
    """Test cases for VectorStore class."""
    
    def test_vector_store_initialization(self):
        """Test VectorStore initialization."""
        vector_store = VectorStore()
        assert vector_store is not None
    
    def test_add_documents(self, mock_vector_store):
        """Test adding documents to vector store."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        documents = [
            {"content": "Document 1", "metadata": {"source": "doc1.txt"}},
            {"content": "Document 2", "metadata": {"source": "doc2.txt"}}
        ]
        
        result = vector_store.add_documents(documents)
        assert result is True
        assert len(vector_store.store.documents) == 2
    
    def test_search_similar_documents(self, mock_vector_store):
        """Test searching for similar documents."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add some documents first
        documents = [
            {"content": "Document about methanol", "metadata": {"source": "doc1.txt"}},
            {"content": "Document about ethanol", "metadata": {"source": "doc2.txt"}}
        ]
        vector_store.store.documents = documents
        
        query = "methanol"
        results = vector_store.search_similar(query, k=2)
        assert len(results) == 2
    
    def test_delete_documents(self, mock_vector_store):
        """Test deleting documents from vector store."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add some documents first
        documents = [
            {"content": "Document 1", "metadata": {"source": "doc1.txt"}},
            {"content": "Document 2", "metadata": {"source": "doc2.txt"}}
        ]
        vector_store.store.documents = documents
        
        result = vector_store.delete_documents(["doc1.txt"])
        assert result is True
        assert len(vector_store.store.documents) == 1
    
    def test_get_document_count(self, mock_vector_store):
        """Test getting document count."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add some documents
        documents = [
            {"content": "Document 1", "metadata": {"source": "doc1.txt"}},
            {"content": "Document 2", "metadata": {"source": "doc2.txt"}}
        ]
        vector_store.store.documents = documents
        
        count = vector_store.get_document_count()
        assert count == 2
    
    def test_clear_vector_store(self, mock_vector_store):
        """Test clearing the vector store."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add some documents first
        documents = [
            {"content": "Document 1", "metadata": {"source": "doc1.txt"}}
        ]
        vector_store.store.documents = documents
        
        result = vector_store.clear()
        assert result is True
        assert len(vector_store.store.documents) == 0
    
    def test_get_document_by_id(self, mock_vector_store):
        """Test getting document by ID."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add a document
        document = {"id": "doc1", "content": "Test content", "metadata": {"source": "doc1.txt"}}
        vector_store.store.documents = [document]
        
        result = vector_store.get_document_by_id("doc1")
        assert result is not None
        assert result["content"] == "Test content"
    
    def test_update_document(self, mock_vector_store):
        """Test updating a document in vector store."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add a document
        document = {"id": "doc1", "content": "Old content", "metadata": {"source": "doc1.txt"}}
        vector_store.store.documents = [document]
        
        updated_doc = {"id": "doc1", "content": "New content", "metadata": {"source": "doc1.txt"}}
        result = vector_store.update_document(updated_doc)
        assert result is True
        
        # Check if document was updated
        doc = vector_store.get_document_by_id("doc1")
        assert doc["content"] == "New content"
    
    def test_search_by_metadata(self, mock_vector_store):
        """Test searching documents by metadata."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add documents with different metadata
        documents = [
            {"content": "Doc 1", "metadata": {"source": "safety.pdf", "category": "safety"}},
            {"content": "Doc 2", "metadata": {"source": "storage.pdf", "category": "storage"}}
        ]
        vector_store.store.documents = documents
        
        results = vector_store.search_by_metadata({"category": "safety"})
        assert len(results) == 1
        assert results[0]["metadata"]["category"] == "safety"
    
    def test_get_statistics(self, mock_vector_store):
        """Test getting vector store statistics."""
        vector_store = VectorStore()
        vector_store.store = mock_vector_store
        
        # Add some documents
        documents = [
            {"content": "Doc 1", "metadata": {"source": "doc1.txt"}},
            {"content": "Doc 2", "metadata": {"source": "doc2.txt"}}
        ]
        vector_store.store.documents = documents
        
        stats = vector_store.get_statistics()
        assert stats is not None
        assert "total_documents" in stats
        assert stats["total_documents"] == 2 