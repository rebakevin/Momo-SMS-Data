import json

from api.auth import is_authenticated
from api.data_parser import DataParser

data_parser = DataParser()


def handle_auth_check(handler):
    if not is_authenticated(handler.headers):
        handler.send_response(401)
        handler.send_header('Content-type', 'application/json')
        handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        handler.end_headers()
        handler.wfile.write(json.dumps(
            {"error": "Unauthorized: Invalid or missing credentials"}).encode())
        return

    handler.send_response(200)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(
        {"message": "Authentication successful"}).encode())


def handle_data_parser(handler):
    if not is_authenticated(handler.headers):
        handler.send_response(401)
        handler.send_header('Content-type', 'application/json')
        handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        handler.end_headers()
        handler.wfile.write(json.dumps(
            {"error": "Unauthorized: Invalid or missing credentials"}).encode())
        return

    try:
        result = data_parser.parse_xml_to_json()
        handler.send_response(200)
        handler.send_header('Content-type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps(result, indent=2).encode())
    except Exception as e:
        handler.send_response(400)
        handler.send_header('Content-type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps({"error": str(e)}).encode())


def get_all_transactions(handler):
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


def delete_transaction(handler, id):
    service = handler.service

    if not service.is_authenticated(handler.headers):
        service.response(handler, 401, {
            "error": "Unauthorized: Invalid or missing credentials"
        })
        return

    success, error, deleted_id = service.delete_transaction(id)
    if not success:
        if "Not Found" in error:
            service.response(handler, 404, {"error": error})
        elif "Bad Request" in error:
            service.response(handler, 400, {"error": error})
        else:
            service.response(handler, 500, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "message": "Transaction deleted successfully",
        "transaction_id": deleted_id
    })


ROUTES = {
    "GET": {
        "/": handle_auth_check,
        "/transactions": get_all_transactions,
        "/transactions/{id}": get_transaction_by_id,
    },
    "POST": {
        "/transactions": create_transaction,
        "/one-time-data-parser": handle_data_parser,
    },
    "DELETE": {
        "/transactions/:id": delete_transaction,
    }
}
