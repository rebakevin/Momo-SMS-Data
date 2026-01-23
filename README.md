# Momo SMS Data API

A Python HTTP API for managing and parsing SMS transaction data with one-time XML to JSON conversion.

## 🌍 Cross-Platform Support

Works on **Windows**, **Linux**, and **macOS**. See [Platform Notes](docs/PLATFORM_NOTES.md) for platform-specific details.

## Features

- ✅ **Basic Authentication**: Secure endpoints with username/password authentication
- ✅ **One-Time Data Parser**: Convert XML data to JSON (can only be executed once)
- ✅ **Auto-Generated OpenAPI Documentation**: Decorator-based documentation system
- ✅ **Interactive Swagger UI**: Test endpoints directly in your browser
- ✅ **XML to JSON Conversion**: Automatic parsing with attribute preservation
- ✅ **Error Handling**: Comprehensive error responses with appropriate HTTP status codes
- ✅ **Modular Architecture**: Clean separation of concerns with dedicated modules

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Momo-SMS-Data
```

2. **(Optional)** Create and activate virtual environment manually:

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

3. **(Optional)** Install dependencies manually:
```bash
pip install -r requirements.txt
```

### Running the Server

**🚀 Recommended: Cross-Platform Python Launcher**

Works on all operating systems (Windows, Linux, macOS):
```bash
python3 run.py
```
or on Windows:
```cmd
python run.py
```

This script automatically:
- ✅ Creates virtual environment if missing
- ✅ Installs dependencies if needed
- ✅ Stops any existing server
- ✅ Starts the API server

**Alternative Methods:**

**Linux/macOS - Bash Script:**
```bash
./run.sh
```

**Manual Start (after activating venv):**

Linux/macOS:
```bash
source venv/bin/activate
python3 main.py
```

Windows:
```cmd
venv\Scripts\activate
python main.py
```

The server will start on `http://localhost:8000`

### Dependencies

- **apispec** (6.3.1): OpenAPI specification generation
- **requests** (2.31.0): HTTP library for testing

All dependencies are specified in [requirements.txt](requirements.txt)

## API Endpoints

### 1. Authentication Check
```
GET /
```
Test your authentication credentials.

### 2. One-Time Data Parser
```
POST /one-time-data-parser
```
Convert XML data from `app/assets/modified_sms_v2.xml` to JSON format. **Can only be called once successfully.**

### 3. Swagger UI Documentation
```
GET /api-docs
```
Interactive Swagger UI interface to explore and test all endpoints.

### 4. OpenAPI JSON Specification
```
GET /openapi.json
```
Get the raw OpenAPI 3.0 JSON specification.

## Quick Start

### Access Swagger UI Documentation

Once the server is running, open your browser and visit:

```
http://localhost:8000/api-docs
```

You'll see an interactive Swagger UI where you can:
- ✅ View all available endpoints
- ✅ See request/response schemas
- ✅ Test endpoints directly from the browser
- ✅ Try out the API with authentication

### Testing with cURL

**1. Check Authentication:**
```bash
curl -X GET http://localhost:8000/ -u admin:admin
```

**2. Parse XML Data (First Time):**
```bash
curl -X POST http://localhost:8000/one-time-data-parser -u admin:admin
```

**3. View API Documentation:**
```bash
curl -X GET http://localhost:8000/api-docs
```

### Using the HTTP Test File

Open `test_main.http` in VS Code with the REST Client extension to test all endpoints interactively.

## Authentication

**Default Credentials:**
- Username: `admin`
- Password: `admin`

**Format:** Basic Authentication
```
Authorization: Basic YWRtaW46YWRtaW4=
```

## Project Structure

```
Momo-SMS-Data/
├── main.py                      # Main API server with auto-doc decorators
├── requirements.txt             # Python dependencies
├── run.py                       # Cross-platform Python launcher ⭐
├── run.sh                       # Linux/macOS bash launcher
├── run.bat                      # Windows batch launcher
├── api/
│   ├── auth.py                  # Authentication module
│   ├── data_parser.py           # XML to JSON parser
│   ├── router.py                # API Router with apispec integration
│   └── README.md                # Parser documentation
├── app/
│   └── assets/
│       └── modified_sms_v2.xml  # Source XML data
├── docs/
│   ├── api_docs.md              # Complete API documentation
│   └── PLATFORM_NOTES.md        # Platform-specific notes ⭐
├── test_main.http               # HTTP test requests
├── venv/                        # Virtual environment (auto-created)
└── README.md                    # This file
```

### Key Files

- **run.py**: Universal launcher for all platforms (Windows/Linux/macOS)
- **router.py**: apispec-based automatic OpenAPI generation
- **requirements.txt**: All required packages
- **PLATFORM_NOTES.md**: Platform-specific instructions and troubleshooting

## Data Parser Details

The data parser:
- Reads XML from `app/assets/modified_sms_v2.xml`
- Converts to nested JSON format
- Preserves XML attributes as `@attributes`
- Creates a `.data_parsed_flag` file after successful parsing
- Prevents duplicate parsing attempts

### XML Format Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sms_transactions>
    <transaction id="1">
        <sender>+256700123456</sender>
        <recipient>+256700987654</recipient>
        <amount currency="UGX">50000</amount>
        <timestamp>2026-01-15T10:30:00Z</timestamp>
        <status>completed</status>
        <reference>TXN001234567</reference>
        <type>mobile_money</type>
    </transaction>
</sms_transactions>
```

### JSON Output Example

```json
{
  "success": true,
  "message": "XML data successfully parsed to JSON",
  "data": {
    "transaction": [
      {
        "@attributes": {
          "id": "1"
        },
        "sender": "+256700123456",
        "recipient": "+256700987654",
        "amount": {
          "@attributes": {
            "currency": "UGX"
          },
          "text": "50000"
        },
        "timestamp": "2026-01-15T10:30:00Z",
        "status": "completed",
        "reference": "TXN001234567",
        "type": "mobile_money"
      }
    ]
  },
  "record_count": 5
}
```

## Response Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid data, already parsed, or parsing error
- `401 Unauthorized`: Missing or invalid credentials
- `404 Not Found`: Route doesn't exist

## Resetting the Parser

To reset the one-time parser flag (for testing):

```bash
rm .data_parsed_flag
```

## Documentation

- [API Documentation](docs/api_docs.md) - Complete endpoint documentation
- [Data Parser README](api/README.md) - Parser module details

## Testing

The project includes a comprehensive test file `test_main.http` with tests for:
- Authentication (with and without credentials)
- API documentation endpoint
- Data parser (first call success)
- Data parser (second call failure)
- Unauthorized access attempts

## Development

### Automatic Documentation System

The API uses a **decorator-based documentation system** that automatically generates OpenAPI specifications:

```python
from api.openapi_generator import api_docs, ResponseSchemas

@api_docs.route(
    path="/endpoint",
    method="get",
    require_auth=True,
    summary="Brief description",
    responses=ResponseSchemas.combined_responses(
        ResponseSchemas.success_message("Success"),
        ResponseSchemas.unauthorized()
    ),
    tags=["Category"]
)
def _handle_endpoint(self):
    """Detailed description from docstring"""
    pass
```

**Benefits:**
- ✅ Documentation and code stay in sync
- ✅ No manual OpenAPI spec editing
- ✅ Consistent response schemas
- ✅ Automatic Swagger UI generation

### Modifying Authentication

Edit [api/auth.py](api/auth.py) to change credentials or authentication logic.

### Adding New Endpoints

Add new route handlers in [main.py](main.py) and update the API documentation in the `_handle_api_docs` method.

### XML Data

Replace or modify [app/assets/modified_sms_v2.xml](app/assets/modified_sms_v2.xml) with your own SMS transaction data.

## License

This project is for educational purposes.

## Author

Enterprise Web Development - Year 2