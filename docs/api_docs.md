# API Documentation

## Momo SMS Data API

Version: 1.0.0

This API provides endpoints for SMS transaction data management and parsing with **automatically generated OpenAPI documentation**.

## 🚀 Key Features

- **Automatic Documentation Generation**: OpenAPI spec is automatically generated from route decorators and docstrings
- **Interactive Swagger UI**: Test endpoints directly from your browser
- **Decorator-Based Routes**: Clean, maintainable route definitions
- **Built-in Authentication**: Basic HTTP authentication for secure endpoints

### Base URL
```
http://localhost:8000
```

### Documentation Architecture

The API uses a **decorator-based documentation system** that automatically generates the OpenAPI 3.0 specification:

1. **Route Decorators**: Each endpoint is decorated with `@api_docs.route()` containing its metadata
2. **Automatic Spec Generation**: The `OpenAPIGenerator` class collects all route information
3. **Dynamic Updates**: Add new endpoints by simply decorating your handler functions
4. **Schema Templates**: Pre-built response schemas for common patterns

#### Example Route Definition

```python
@api_docs.route(
    path="/one-time-data-parser",
    method="post",
    require_auth=True,
    summary="Parse XML data to JSON (One-time only)",
    description="Converts XML data from app/assets/modified_sms_v2.xml to JSON format.",
    responses=ResponseSchemas.combined_responses(
        ResponseSchemas.success_message("Data parsed successfully"),
        ResponseSchemas.bad_request("Already parsed"),
        ResponseSchemas.unauthorized()
    ),
    tags=["Data Management"]
)
def _handle_data_parser(self):
    """Handler implementation"""
    pass
```

### Authentication

All endpoints (except `/api-docs` and `/openapi.json`) require Basic Authentication.

**Credentials:**
- Username: `admin`
- Password: `admin`

**Header Format:**
```
Authorization: Basic YWRtaW46YWRtaW4=
```

---

## Endpoints

### 1. Authentication Check

**Endpoint:** `GET /`

**Tags:** Authentication

**Description:** Verify basic authentication credentials

**Authentication:** Required

**Response:**

**Success (200):**
```json
{
  "message": "Authentication successful"
}
```

**Error (401):**
```json
{
  "error": "Unauthorized: Invalid or missing credentials"
}
```

---

### 2. One-Time Data Parser

**Endpoint:** `POST /one-time-data-parser`

**Tags:** Data Management

**Description:** Converts XML data from `app/assets/modified_sms_v2.xml` to JSON format. 

**⚠️ IMPORTANT:** This endpoint can only be called **once** successfully. Subsequent calls will return an error.

**Authentication:** Required

**Response:**

**Success (200):**
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

**Error (400) - Already Parsed:**
```json
{
  "error": "Data has already been parsed. This endpoint can only be called once."
}
```

**Error (401):**
```json
{
  "error": "Unauthorized: Invalid or missing credentials"
}
```

---

### 3. Swagger UI Documentation

**Endpoint:** `GET /api-docs`

**Tags:** Documentation

**Description:** Interactive Swagger UI interface to explore and test all available API endpoints

**Authentication:** Not Required

**Response:**

Returns an HTML page with the Swagger UI interface for interactive API exploration.

---

### 4. OpenAPI JSON Specification

**Endpoint:** `GET /openapi.json`

**Tags:** Documentation

**Description:** Get the raw OpenAPI 3.0 JSON specification for all available endpoints

**Authentication:** Not Required

**Response:**

**Success (200):**
Returns the complete OpenAPI 3.0 specification automatically generated from route decorators.

---

## 📝 Adding New Endpoints

To add a new endpoint to the API with automatic documentation:

1. **Import the decorator**:
```python
from api.openapi_generator import api_docs, ResponseSchemas
```

2. **Define your route handler**:
```python
@api_docs.route(
    path="/your-endpoint",
    method="get",
    require_auth=True,
    summary="Brief description",
    description="Detailed description",
    responses=ResponseSchemas.combined_responses(
        ResponseSchemas.success_message("Success"),
        ResponseSchemas.unauthorized()
    ),
    tags=["Your Category"]
)
def _handle_your_endpoint(self):
    """
    Your endpoint logic here.
    This docstring becomes part of the API documentation.
    """
    # Implementation
    pass
```

3. **Register the route**:
```python
cls.routes['GET']['/your-endpoint'] = cls._handle_your_endpoint
```

4. **Done!** The OpenAPI spec is automatically updated.

---

## Usage Examples

### cURL Examples

**1. Check Authentication:**
```bash
curl -X GET http://localhost:8000/ \
  -u admin:admin
```

**2. Parse Data (First Time):**
```bash
curl -X POST http://localhost:8000/one-time-data-parser \
  -u admin:admin
```

**3. Get OpenAPI Specification:**
```bash
curl -X GET http://localhost:8000/openapi.json
```

**4. Access Swagger UI:**
```bash
# Open in browser
http://localhost:8000/api-docs
```

### Python Example

```python
import requests
from requests.auth import HTTPBasicAuth

base_url = "http://localhost:8000"
auth = HTTPBasicAuth('admin', 'admin')

# Parse data
response = requests.post(
    f"{base_url}/one-time-data-parser",
    auth=auth
)

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['message']}")
    print(f"Records parsed: {data['record_count']}")
else:
    print(f"Error: {response.json()['error']}")
```

---

## OpenAPI Generator Module

The `api/openapi_generator.py` module provides:

### OpenAPIGenerator Class

- **Purpose**: Automatically generate OpenAPI 3.0 specifications
- **Features**:
  - Decorator-based route registration
  - Automatic spec generation
  - Support for authentication, tags, and response schemas
  
### ResponseSchemas Class

Pre-built response schema templates:
- `success_message(message)` - Standard success response
- `error_response(code, message)` - Error response
- `unauthorized()` - 401 Unauthorized
- `bad_request(message)` - 400 Bad Request
- `not_found(message)` - 404 Not Found
- `combined_responses(*dicts)` - Combine multiple responses

---

## Error Handling

All errors return appropriate HTTP status codes:

- **400 Bad Request**: Invalid data, already parsed, or parsing errors
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Route doesn't exist

---

## Benefits of Auto-Generated Documentation

✅ **Single Source of Truth**: Code and documentation always in sync  
✅ **Less Maintenance**: Update decorators instead of separate docs  
✅ **Type Safety**: Schema validation at definition time  
✅ **Discoverability**: All endpoints visible in Swagger UI  
✅ **Consistency**: Standardized response formats  
✅ **Extensibility**: Easy to add new endpoints  

---

## Notes

- The server runs on port 8000 by default
- All responses are in JSON format (except Swagger UI which is HTML)
- OpenAPI specification is dynamically generated on each request
- Route decorators are executed at module import time
- XML attributes are preserved as `@attributes` in JSON output

## Momo SMS Data API

Version: 1.0.0

This API provides endpoints for SMS transaction data management and parsing.

### Base URL
```
http://localhost:8000
```

### Authentication

All endpoints (except `/api-docs`) require Basic Authentication.

**Credentials:**
- Username: `admin`
- Password: `admin`

**Header Format:**
```
Authorization: Basic YWRtaW46YWRtaW4=
```

---

## Endpoints

### 1. Authentication Check

**Endpoint:** `GET /`

**Description:** Verify basic authentication credentials

**Authentication:** Required

**Response:**

**Success (200):**
```json
{
  "message": "Authentication successful"
}
```

**Error (401):**
```json
{
  "error": "Unauthorized: Invalid or missing credentials"
}
```

---

### 2. One-Time Data Parser

**Endpoint:** `POST /one-time-data-parser`

**Description:** Converts XML data from `app/assets/modified_sms_v2.xml` to JSON format. 

**⚠️ IMPORTANT:** This endpoint can only be called **once** successfully. Subsequent calls will return an error.

**Authentication:** Required

**Response:**

**Success (200):**
```json
{
  "success": true,
  "message": "XML data successfully parsed to JSON",
  "data": {
    "sms_transactions": {
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
    }
  },
  "record_count": 5
}
```

**Error (400) - Already Parsed:**
```json
{
  "error": "Data has already been parsed. This endpoint can only be called once."
}
```

**Error (400) - Empty File:**
```json
{
  "error": "XML file is empty. Please add data to the file first."
}
```

**Error (400) - Parse Error:**
```json
{
  "error": "Error parsing XML: <error details>"
}
```

**Error (401):**
```json
{
  "error": "Unauthorized: Invalid or missing credentials"
}
```

---

### 3. API Documentation

**Endpoint:** `GET /api-docs`

**Description:** Returns OpenAPI 3.0 specification for all available endpoints

**Authentication:** Not Required

**Response:**

**Success (200):**
Returns a JSON object containing the complete OpenAPI specification with all endpoints, schemas, and security requirements.

---

## Usage Examples

### cURL Examples

**1. Check Authentication:**
```bash
curl -X GET http://localhost:8000/ \
  -u admin:admin
```

**2. Parse Data (First Time):**
```bash
curl -X POST http://localhost:8000/one-time-data-parser \
  -u admin:admin
```

**3. Get API Documentation:**
```bash
curl -X GET http://localhost:8000/api-docs
```

### Python Example

```python
import requests
from requests.auth import HTTPBasicAuth

# Base URL
base_url = "http://localhost:8000"

# Credentials
auth = HTTPBasicAuth('admin', 'admin')

# Parse data
response = requests.post(
    f"{base_url}/one-time-data-parser",
    auth=auth
)

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['message']}")
    print(f"Records parsed: {data['record_count']}")
else:
    print(f"Error: {response.json()['error']}")
```

---

## Data Parser Details

### How It Works

1. **XML File Location:** The parser reads from `app/assets/modified_sms_v2.xml`
2. **Conversion:** XML structure is converted to nested JSON objects
3. **One-Time Flag:** After successful parsing, a `.data_parsed_flag` file is created
4. **Subsequent Calls:** The flag file prevents re-parsing

### XML Structure Expected

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
    <!-- More transactions... -->
</sms_transactions>
```

### Resetting the Parser (Development Only)

If you need to reset the one-time restriction for testing:

```bash
rm /path/to/project/.data_parsed_flag
```

---

## Error Handling

All errors return appropriate HTTP status codes and JSON error messages:

- **400 Bad Request:** Invalid data, already parsed, or parsing errors
- **401 Unauthorized:** Missing or invalid authentication
- **404 Not Found:** Route doesn't exist
- **500 Internal Server Error:** Unexpected server errors

---

## Notes

- The server runs on port 8000 by default
- All responses are in JSON format
- XML attributes are preserved as `@attributes` in the JSON output
- The parser handles nested XML structures recursively
- Empty or whitespace-only text nodes are ignored
