# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Main application entry point
python run.py

# Development mode with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Using uv (preferred package manager)
uv run python run.py
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Testing
```bash
# Comprehensive automated tests
python test/test_syslog.py

# Full integration tests with debug server
python test/run_full_test.py

# Interactive UI test tool
python test/ui_test_tool.py

# Debug syslog server (for testing message transmission)
python test/debug_syslog_server.py
```

### Docker Commands
```bash
# Build and run with docker-compose
docker-compose up -d

# Run with debug syslog server
docker-compose --profile debug up -d

# Build only the main application
docker build -t syslog-tester .

# Run container manually
docker run -d -p 8001:8001 -v $(pwd)/data:/app/data syslog-tester

# View logs
docker-compose logs -f syslog-tester

# Stop services
docker-compose down
```

### Package Management
This project uses `uv` as the preferred package manager with fallback to `pip`:
- Dependencies: `pyproject.toml` (primary) and `requirements.txt` (fallback)
- Virtual environment in `.venv/`

## Application Architecture

### Core Structure
- **FastAPI Application**: Modern async web framework serving both API and static files
- **RFC Standards Support**: Complete RFC 3164 and RFC 5424 syslog message parsing/generation
- **Modular Design**: Clean separation of concerns across parsers, generators, senders, and models

### Key Directories
- `app/core/`: Configuration and database management
- `app/models/`: Pydantic data models for validation
- `app/parsers/`: RFC-compliant message parsing (rfc3164.py, rfc5424.py)  
- `app/generators/`: Message generation services
- `app/senders/`: Network transmission (UDP/TCP)
- `app/routers/`: FastAPI route handlers
- `static/`: Frontend assets (HTML/CSS/JavaScript)

### Database
- SQLite database (`examples.db`) for storing user-defined message examples
- SQLAlchemy ORM with Alembic migrations support
- Database initialization handled automatically on startup

### Application Ports & URLs
- Default port: 8001
- Web interface: http://localhost:8001
- API documentation: http://localhost:8001/docs
- Health check: http://localhost:8001/health

## Syslog Implementation Details

### Supported RFC Standards
- **RFC 3164**: Traditional BSD syslog format
- **RFC 5424**: New standardized syslog protocol

### Message Components
- Priority calculation: `Facility × 8 + Severity`
- Timestamp formats: Both RFC 3164 (BSD) and RFC 5424 (ISO 8601) supported
- Structured data support in RFC 5424 messages
- Dynamic message component system with key-value pairs

### Network Transmission
- UDP and TCP protocol support  
- Configurable transmission count (1-10,000) with unlimited mode
- Real-time progress tracking and error handling
- Default test server: 127.0.0.1:5140

## Test Infrastructure

### Test Types
1. **Automated Tests** (`test_syslog.py`): Comprehensive RFC compliance validation
2. **Integration Tests** (`run_full_test.py`): Full system testing with message transmission
3. **Interactive Testing** (`ui_test_tool.py`): Manual test case execution
4. **Debug Server** (`debug_syslog_server.py`): Message reception verification

### Test Results
- `test_results.json`: Detailed automated test results
- `received_messages.json`: Debug server message log
- Current test coverage: 77.8% success rate (improvements ongoing)

### Common Test Scenarios
- Message generation and parsing validation
- Priority calculation verification
- Timestamp format compliance
- Network transmission testing (UDP/TCP)
- Structured data parsing (RFC 5424)

## Development Notes

### Configuration
- Settings in `app/core/config.py` using Pydantic BaseSettings
- Environment variable support via `.env` file
- Debug mode affects uvicorn auto-reload behavior

### Frontend Integration  
- Single-page application with vanilla JavaScript
- Real-time progress updates via polling
- Responsive 3-column layout (examples, configuration, results)
- Example management with SQLite persistence

### Code Style
- Korean comments in code (maintain existing pattern)
- Type hints throughout codebase
- Pydantic models for data validation
- FastAPI dependency injection patterns