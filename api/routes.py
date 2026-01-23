def get_transactions(handler):
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    transactions = service.read_transactions()
    service.response(handler, 200, transactions)


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


ROUTES = {
    "GET": {
        "/transactions": get_transactions,
    },
    "POST": {
        "/transactions": create_transaction,
    }
}
