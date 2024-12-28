# Simple Library Management System

This project is a web-based library management system built with Quart, providing APIs for managing books, readers, and loans.

The Simple Library Management System is a lightweight application designed to help librarians and library staff manage their book inventory, reader records, and book loans efficiently. It offers a set of RESTful APIs and web interfaces for performing common library management tasks.

Key features of the system include:
- Book management: Add new books, retrieve book information, and search for books by ID or title.
- Reader management: Register new readers, view reader information, and search for readers by ID or name.
- Loan management: Create new loans, view active loans, return books, and track loan history.
- Data persistence: All data is stored in a SQLite database.
- Web interface: Some operations are accessible through HTML templates for a user-friendly experience.

## Repository Structure

The repository is organized as follows:

- `app.py`: The main application file containing all route definitions and business logic.
- `migrations/0.py`: Database migration script for setting up the initial schema.
- `templates/`: Directory containing HTML templates for web pages.
  - `active_loans.html`: Template for displaying active loans.
  - `base.html`: Base template for other HTML pages.
  - `display_books.html`: Template for displaying book information.
  - `home.html`: Template for the home page.
  - `readers.html`: Template for displaying reader information.

## Usage Instructions

### Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Clone the repository to your local machine.
3. Navigate to the project directory:
   ```
   cd library-simple
   ```
4. Install the required dependencies:
   ```
   pip install quart quart-db quart-schema
   ```

### Getting Started

1. Initialize the database by running the migration script:
   ```
   python -m quart_db upgrade
   ```
2. Start the Quart development server:
   ```
   python app.py
   ```
3. The application will be available at `http://localhost:5000`.

### API Endpoints

#### Books

- `POST /books/`: Create a new book
- `GET /books1/`: Get all books
- `GET /books/<int:id>/`: Get a book by ID
- `GET /books/<string:title>/`: Get a book by title

#### Readers

- `POST /readers/`: Create a new reader
- `GET /readers/`: Get all readers (HTML page)
- `GET /readers/<int:id>/`: Get a reader by ID
- `GET /readers/<string:name>/`: Get a reader by name

#### Loans

- `POST /loans/`: Create a new loan
- `GET /loans/`: Get all loans (HTML page)
- `GET /api/loans/`: Get all loans (JSON API)
- `GET /loans/<int:id>/`: Get a loan by ID
- `POST /loans/<int:loan_id>/return/`: Return a borrowed book

#### Reader Books

- `GET /readers/<int:reader_id>/books/`: Get a reader's borrowed books

### Configuration

The application uses a SQLite database by default. You can change the database URL in the `app.py` file:

```python
QuartDB(app, url="sqlite:///database.db")
```

#### Performance Optimization

- Monitor database query performance using SQLite's built-in query planner.
- Use appropriate indexing on frequently queried columns in the database.
- Implement caching for frequently accessed data to reduce database load.

## Data Flow

The Simple Library Management System follows a straightforward request-response cycle:

1. Client sends a request to one of the API endpoints.
2. The Quart application receives the request and routes it to the appropriate handler.
3. The handler function processes the request, interacting with the database as needed.
4. The database returns the requested data or confirms the requested action.
5. The handler function formats the response (JSON for API calls, HTML for web pages).
6. The response is sent back to the client.

```
[Client] <--> [Quart App] <--> [SQLite Database]
   ^             |
   |             v
   +--- [HTML Templates (for web pages)]
```

Note: The application uses Quart-DB for database connections and Quart-Schema for request/response validation, enhancing data integrity and API reliability.


## Further refactoring

Planned improvements for the library management system:

1. Code Structure
   - Implement Flask Blueprint to separate routes by domain (books, readers, loans)
   - Move models to a dedicated models/ directory
   - Create separate service layer for business logic
   - Add configuration management for different environments

2. Authentication & Authorization
   - Implement user authentication system
   - Add password hashing with salt using bcrypt
   - Create two user roles: library admin and reader
   - Implement role-based access control (RBAC)
   - Add session management

3. Frontend Improvements
   - Consider migrating to React for improved user experience
   - Implement real-time updates for loan status
   - Add responsive design for mobile devices
   - Create separate admin and reader dashboards

4. Additional Features
   - Add email notifications for due dates
   - Implement book reservation system
   - Add book categories and search functionality
   - Create reader profile pages
   - Add loan history and statistics

5. Security Enhancements
   - Add input validation and sanitization
   - Implement CSRF protection
   - Add rate limiting for API endpoints
   - Implement secure password reset flow
