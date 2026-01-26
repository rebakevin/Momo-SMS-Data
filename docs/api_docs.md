# API Docs

### POST `/transactions`
<details>
<summary>Click to expand</summary>

When making the POST request you have to provide a JSON object that looks like this:
```json
{
  "sender": "name (string)",
  "amount_rwf": 0,
  "type": "received or sent (string)",
  "from": "name (string)",
  "phone": "phone number (string)"
}
```

If the request is succesful you will receive a JSON response object:
```json
{
    "status": "success",
    "message": "Transaction created successfully",
    "data": {
        "sender": "M-Money",
        "amount_rwf": 10000,
        "type": "received",
        "from": "Kevin Rebakure",
        "phone_masked": "*******630",
        "transaction_id": 4,
        "date": "2026-01-26T08:39:04",
        "readable_date": "26 Jan 2026 08:39:04 AM",
        "balance_rwf": 40000
    }
}
```

- Notice that the phone number is masked and the date of the transaction is properly recorded both in timestamp and human readable format.
- The balance is calculated. When you send money, the balance will be reduced and when you receive money the balance will be increased.
- You will receive a `201 CREATED` status code
- Validation errors will be represented with this JSON object
```json
    {
        "error": "Bad Request: Missing required fields (from, phone)"
    }
```

</details>

### GET `/transactions` and `/transactions/{id}`
<details>
<summary>Click to expand</summary>

[Deborah - Documentation]

</details>

### PATCH `/transactions/{id}`
<details>
<summary>Click to expand</summary>

[Victor - Documentation]

</details>

### DELETE `/transactions/{id}`
<details>
<summary>Click to expand</summary>

[Elie - Documentation]

</details>

### POST `/one-time-data-parser`
<details>
<summary>Click to expand</summary>

- Converts XML data from `app/assets/modified_sms_v2.xml` to JSON format. 
- ⚠️ **IMPORTANT:** This endpoint can only be called **once** successfully. Subsequent calls will return an error.
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

</details>

### GET `/api-docs`
<details>
<summary>Click to expand</summary>

- Swagger UI Documentation
- Returns an HTML page with the Swagger UI interface for interactive API exploration.

</details>

### GET `/openapi.json`
<details>
<summary>Click to expand</summary>

- Get the raw OpenAPI 3.0 JSON specification for all available endpoints
- Returns the complete OpenAPI 3.0 specification automatically generated from route decorators.

</details>