# API Docs

## POST `/transactions`
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

- Notice that the phone number is masked and the date of the transaction is properly recorded both in timestampa and human readbale format.
- The balance is calculated. When you send money, the balance will be reduced and when you receive money the balance will be increased.
- You will receive a `201 CREATED` status code
- Validation errors will be represented with this JSON object
    ```json
    {
        "error": "Bad Request: Missing required fields (from, phone)"
    }
    ```

## GET `/transactions` and `/transactios/{id}`

[Deborah - Documentation]

## PATCH `/transactions/{id}`

[Victor - Documentation]

## DELETE `/transactions/{id}`

[Elie - Documentation]