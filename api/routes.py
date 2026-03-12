import json

from api.auth import is_authenticated
from api.data_parser import DataParser

data_parser = DataParser()


def send_auth_error(handler):
    handler.send_response(401)
    handler.send_header('Content-type', 'application/json')
    handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
    handler.end_headers()
    handler.wfile.write(json.dumps(
        {"error": "Unauthorized: Invalid or missing credentials"}).encode())


def handle_auth_check(handler):
    success, user_id = handler.service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id
    handler.send_response(200)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(
        {"message": "Authentication successful"}).encode())


def handle_data_parser(handler):
    success, user_id = handler.service.is_authenticated(handler.headers)
    if not success:
        handler.send_response(401)
        handler.send_header('Content-type', 'application/json')
        handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        handler.end_headers()
        handler.wfile.write(json.dumps(
            {"error": "Unauthorized: Invalid or missing credentials"}).encode())
        return

    handler.user_id = user_id

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

    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    success, error, transactions = service.get_all_transactions(user_id=user_id)
    if not success:
        service.response(handler, 500, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "data": transactions
    })


def create_transaction(handler):
    service = handler.service

    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    is_valid, error, data = service.validate_create_transaction_request(
        handler.headers,
        handler.rfile
    )

    if not is_valid:
        service.response(handler, 400, {"error": error})
        return

    success, error, created_data = service.write_transaction(data, user_id=user_id)
    if not success:
        service.response(handler, 500, {"error": error})
        return

    service.response(handler, 201, {
        "status": "success",
        "message": "Transaction created successfully",
        "data": created_data
    })


def get_transaction_by_id(handler, id):
    service = handler.service

    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    transaction_id = id

    success, error, transaction = service.get_transaction_by_id(transaction_id, user_id=user_id)
    if not success:
        status_code = 404 if "Not Found" in error else 400
        service.response(handler, status_code, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "data": transaction
    })


def update_transaction(handler, id):
    service = handler.service

    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    is_valid, error, data = service.validate_update_transaction_request(
        handler.headers,
        handler.rfile
    )

    if not is_valid:
        service.response(handler, 400, {"error": error})
        return

    success, error, updated_transaction = service.update_transaction(id, data, user_id=user_id)
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
        "message": "Transaction updated successfully",
        "data": updated_transaction
    })


def delete_transaction(handler, id):
    service = handler.service

    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    success, error, deleted_id = service.delete_transaction(id, user_id=user_id)
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


def get_all_logs(handler):
    service = handler.service
    
    success, user_id = service.is_authenticated(handler.headers)
    if not success:
        send_auth_error(handler)
        return

    handler.user_id = user_id

    success, error, logs = service.get_all_logs()
    if not success:
        service.response(handler, 500, {"error": error})
        return

    service.response(handler, 200, {
        "status": "success",
        "data": logs
    })


ROUTES = {
    "GET": {
        "/": handle_auth_check,
        "/transactions": get_all_transactions,
        "/transactions/:id": get_transaction_by_id,
        "/logs": get_all_logs,
    },
    "POST": {
        "/transactions": create_transaction,
        "/one-time-data-parser": handle_data_parser,
    },
    "PUT": {
        "/transactions/:id": update_transaction,
    },
    "DELETE": {
        "/transactions/:id": delete_transaction,
    }
}