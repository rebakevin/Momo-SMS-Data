# Data Parser Module

## Overview

The Data Parser module is responsible for converting XML data from the assets folder into JSON format. It includes a one-time execution restriction to ensure data is only imported once.

## Features

- **XML to JSON Conversion**: Automatically converts XML structure to nested JSON objects
- **One-Time Execution**: Prevents duplicate data imports with a flag file system
- **Attribute Preservation**: XML attributes are maintained in the JSON output as `@attributes`
- **Recursive Parsing**: Handles complex nested XML structures
- **Error Handling**: Comprehensive error handling for file and parsing issues

## File Structure

```
api/
├── data_parser.py       # Main data parser module
└── auth.py             # Authentication module

app/
└── assets/
    └── modified_sms_v2.xml  # Source XML file
```

## Usage

### Importing the Module

```python
from api.data_parser import DataParser

# Create parser instance
parser = DataParser()
```

### Parsing Data

```python
try:
    result = parser.parse_xml_to_json()
    print(f"Success: {result['message']}")
    print(f"Records: {result['record_count']}")
    print(f"Data: {result['data']}")
except Exception as e:
    print(f"Error: {str(e)}")
```

### Checking Parse Status

```python
# Check if data has already been parsed
if parser.has_been_parsed():
    print("Data has already been parsed")
else:
    print("Data not yet parsed")
```

### Resetting (Development Only)

```python
# Reset the parse flag for testing
parser.reset_parse_flag()
```

## API Endpoint

The parser is exposed via the API endpoint:

```
POST /one-time-data-parser
```

**Authentication Required**: Basic Auth (admin:admin)

**Response Example:**

```json
{
  "success": true,
  "message": "XML data successfully parsed to JSON",
  "data": {
    "sms_transactions": {
      "transaction": [...]
    }
  },
  "record_count": 5
}
```

## XML Format

The parser expects XML in the following format:

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

## JSON Output Format

XML attributes become nested objects with `@attributes` key:

```json
{
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
}
```

## Error Handling

The parser handles several error conditions:

1. **Already Parsed**: Returns error if data has been previously parsed
2. **File Not Found**: Returns error if XML file doesn't exist
3. **Empty File**: Returns error if XML file is empty
4. **Parse Error**: Returns detailed XML parsing errors

## Flag File

The parser uses a `.data_parsed_flag` file in the project root to track whether data has been parsed. This file is created automatically after successful parsing.

To reset for testing:

```bash
rm .data_parsed_flag
```

## Class Methods

### `__init__()`
Initializes the parser with file paths and state.

### `has_been_parsed()`
Returns `True` if data has been previously parsed.

### `mark_as_parsed()`
Creates the flag file to indicate successful parsing.

### `parse_xml_to_json()`
Main parsing method. Returns dictionary with parsed data.

### `get_parsed_data()`
Returns the most recently parsed data.

### `reset_parse_flag()`
Removes the flag file (for testing only).

## Dependencies

- `xml.etree.ElementTree`: XML parsing
- `json`: JSON operations
- `os`: File operations
- `pathlib`: Path handling
