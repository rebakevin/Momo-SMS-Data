def get_transactions(handler):
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    transactions = service.read_transactions()
    service.response(handler, 200, transactions)


def get_all_transactions(handler):
    """Controller handler to retrieve all transactions."""
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    success, error, transactions = service.get_all_transactions()
    if not success:
        service.response(handler, 500, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "data": transactions
    })


def create_transaction(handler):
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    is_valid, error, data = service.validate_create_transaction_request(
        handler.headers,
        handler.rfile
    )

    if not is_valid:
        service.response(handler, 400, {"error": error})
        return

    success, error = service.write_transaction(data)
    if not success:
        service.response(handler, 500, {"error": error})
        return

    service.response(handler, 201, {
        "status": "success",
        "message": "Transaction created successfully",
        "data": data
    })


def get_transaction_by_id(handler):
    """Controller handler to retrieve a transaction by ID."""
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    # Extract transaction ID from path (e.g., /transactions/123)
    path_parts = handler.path.split('/')
    if len(path_parts) < 3:
        service.response(handler, 400, {"error": "Bad Request: Invalid path"})
        return
    
    transaction_id = path_parts[2]
    
    success, error, transaction = service.get_transaction_by_id(transaction_id)
    if not success:
        status_code = 404 if "Not Found" in error else 400
        service.response(handler, status_code, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "data": transaction
    })


ROUTES = {
    "GET": {
        "/transactions": get_transactions,
        "/transactions/all": get_all_transactions,
        "/transactions/{id}": get_transaction_by_id
    },
    "POST": {
        "/transactions": create_transaction,
    }
}
