from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from quart import Quart


@pytest.fixture
def app():
    """Create a test Quart application."""
    app = Quart(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def test_books():
    """Sample book data for testing."""
    return [
        {"id": 1, "title": "Test Book 1", "author": "Author One"},
        {"id": 2, "title": "Test Book 2", "author": "Author Two"},
    ]


@pytest.fixture
def test_loans():
    """Sample loan data for testing."""
    return [
        {
            "id": 1,
            "book_id": 1,
            "reader_id": 1,
            "loan_date": "2024-01-01",
            "due_date": "2024-01-15",
            "returned": False,
            "book_title": "Test Book 1",
            "reader_name": "John Doe",
        },
        {
            "id": 2,
            "book_id": 2,
            "reader_id": 2,
            "loan_date": "2024-01-02",
            "due_date": "2024-01-16",
            "returned": True,
            "book_title": "Test Book 2",
            "reader_name": "Jane Doe",
        },
    ]


@pytest.fixture
def test_readers():
    """Sample reader data for testing."""
    return [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Doe"}]


class TestBooks:
    """Tests for book-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_books(self, app, test_books):
        """Test GET /books/ endpoint"""
        async with app.test_client() as client:
            with patch(
                "quart.g.connection.iterate", new_callable=AsyncMock
            ) as mock_iterate:
                mock_iterate.return_value = test_books

                response = await client.get("/books/")

                assert response.status_code == 200
                data = await response.get_json()

                assert len(data["books"]) == 2
                assert data["books"][0]["title"] == "Test Book 1"
                assert data["books"][1]["title"] == "Test Book 2"

                mock_iterate.assert_called_once()
                query = mock_iterate.call_args[0][0]
                assert "SELECT" in query
                assert "FROM books" in query

    @pytest.mark.asyncio
    async def test_get_books_empty(self, app):
        """Test GET /books/ endpoint with no books"""
        async with app.test_client() as client:
            with patch(
                "quart.g.connection.iterate", new_callable=AsyncMock
            ) as mock_iterate:
                mock_iterate.return_value = []

                response = await client.get("/books/")

                assert response.status_code == 200
                data = await response.get_json()
                assert len(data["books"]) == 0


class TestLoans:
    """Tests for loan-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_loans_page(self, app, test_loans):
        """Test GET /loans/ endpoint (HTML template)"""
        async with app.test_client() as client:
            with patch(
                "quart.g.connection.iterate", new_callable=AsyncMock
            ) as mock_iterate:
                mock_iterate.return_value = test_loans

                response = await client.get("/loans/")

                assert response.status_code == 200
                html_content = await response.get_data(as_text=True)

                assert "Test Book 1" in html_content
                assert "John Doe" in html_content
                assert "2024-01-15" in html_content

                mock_iterate.assert_called_once()
                query = mock_iterate.call_args[0][0]
                assert "JOIN books" in query
                assert "JOIN readers" in query

    @pytest.mark.asyncio
    async def test_get_loans_page_empty(self, app):
        """Test GET /loans/ endpoint with no loans"""
        async with app.test_client() as client:
            with patch(
                "quart.g.connection.iterate", new_callable=AsyncMock
            ) as mock_iterate:
                mock_iterate.return_value = []

                response = await client.get("/loans/")

                assert response.status_code == 200
                html_content = await response.get_data(as_text=True)
                assert "No active loans" in html_content


class TestReaders:
    """Tests for reader-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_readers(self, app, test_readers):
        """Test GET /readers/ endpoint"""
        async with app.test_client() as client:
            with patch(
                "quart.g.connection.iterate", new_callable=AsyncMock
            ) as mock_iterate:
                mock_iterate.return_value = test_readers

                response = await client.get("/readers/")

                assert response.status_code == 200
                html_content = await response.get_data(as_text=True)

                assert "John Doe" in html_content
                assert "Jane Doe" in html_content

                mock_iterate.assert_called_once()
                query = mock_iterate.call_args[0][0]
                assert "SELECT" in query
                assert "FROM readers" in query


def test_app_configuration(app):
    """Test application configuration"""
    assert app.config["TESTING"] is True
