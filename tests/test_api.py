import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Test client
client = TestClient(app)

# Mock data
TEST_WALLET_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
TEST_SIGNATURE = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
TEST_ARTICLE_URL = "https://example.com/article"
TEST_SUMMARY = "This is a test summary of an article."
TEST_ORIGINAL_CONTENT = "This is the original content of the article. It is longer than the summary."


# Setup and teardown for tests
@pytest.fixture(scope="function")
def test_db():
    # Create in-memory SQLite database for testing
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Dependency override
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)
    
    # Remove override
    app.dependency_overrides.clear()


class TestSummaryEndpoints:
    
    @patch("app.services.web3_service.verify_signature", return_value=True)
    @patch("app.services.scraper_service.scrape_article")
    @patch("app.services.summarizer_service.summarizer.summarize_text")
    def test_summarize_article(self, mock_summarize, mock_scrape, mock_verify, test_db):
        # Setup mocks
        mock_scrape.return_value = TEST_ORIGINAL_CONTENT
        mock_summarize.return_value = TEST_SUMMARY
        
        # Test data
        payload = {
            "wallet_address": TEST_WALLET_ADDRESS,
            "signature": TEST_SIGNATURE,
            "article_url": TEST_ARTICLE_URL
        }
        
        # Make request
        response = client.post("/api/summarize", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["wallet_address"] == TEST_WALLET_ADDRESS
        assert data["article_url"] == TEST_ARTICLE_URL
        assert data["summary_content"] == TEST_SUMMARY
        
    @patch("app.services.web3_service.verify_signature", return_value=False)
    def test_summarize_invalid_signature(self, mock_verify, test_db):
        # Test data
        payload = {
            "wallet_address": TEST_WALLET_ADDRESS,
            "signature": "invalid_signature",
            "article_url": TEST_ARTICLE_URL
        }
        
        # Make request
        response = client.post("/api/summarize", json=payload)
        
        # Assert
        assert response.status_code == 401
        assert "Invalid signature" in response.json()["detail"]
    
    # Additional tests could be added here
