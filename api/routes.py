"""
API Routes and Documentation System
Contains route handlers and OpenAPI documentation generation using apispec
"""

from apispec import APISpec
from functools import wraps
import json
from api.auth import is_authenticated
from api.data_parser import DataParser


class APIRouter:
    """
    Unified router and OpenAPI documentation system using apispec.
    Single source of truth for routing and documentation.
    """

    def __init__(self, title, version, openapi_version="3.0.3", description=""):
        """Initialize APISpec and route registry"""
        self.spec = APISpec(
            title=title,
            version=version,
            openapi_version=openapi_version,
            info={"description": description}
        )

        self.spec.components.security_scheme(
            "basicAuth",
            {
                "type": "http",
                "scheme": "basic",
                "description": "Basic HTTP authentication"
            }
        )

        self.routes = {}

    def route(self, path, methods=None, summary="", description="",
              require_auth=False, responses=None, tags=None, parameters=None):
        """
        Decorator to register route and OpenAPI documentation.

        Args:
            path: API endpoint path
            methods: List of HTTP methods (e.g., ['GET', 'POST'])
            summary: Brief endpoint description
            description: Detailed endpoint description
            require_auth: Whether endpoint requires authentication
            responses: Dict of response codes and descriptions
            tags: List of tags for grouping endpoints
            parameters: List of parameter definitions for path/query parameters
        """
        if methods is None:
            methods = ['GET']

        if responses is None:
            responses = {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }

        def decorator(handler):

            for method in methods:
                method_upper = method.upper()
                if method_upper not in self.routes:
                    self.routes[method_upper] = {}
                self.routes[method_upper][path] = handler

            operation = {
                "summary": summary or handler.__name__.replace("_", " ").title(),
                "description": description or handler.__doc__ or "",
                "responses": responses
            }

            if tags:
                operation["tags"] = tags

            if parameters:
                operation["parameters"] = parameters

            if require_auth:
                operation["security"] = [{"basicAuth": []}]

                if "401" not in responses:
                    responses["401"] = {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {
                                            "type": "string",
                                            "example": "Unauthorized: Invalid or missing credentials"
                                        }
                                    }
                                }
                            }
                        }
                    }

            for method in methods:
                self.spec.path(
                    path=path,
                    operations={method.lower(): operation}
                )

            @wraps(handler)
            def wrapper(*args, **kwargs):
                return handler(*args, **kwargs)

            return wrapper

        return decorator

    def get_openapi_spec(self):
        """Get OpenAPI specification as dictionary"""
        return self.spec.to_dict()

    def get_openapi_json(self, indent=2):
        """Get OpenAPI specification as JSON string"""
        return json.dumps(self.get_openapi_spec(), indent=indent)

    def get_swagger_ui_html(self, openapi_url="/openapi.json"):
        """
        Generate minimal Swagger UI HTML that loads spec from URL.
        No inline OpenAPI content.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui.css">
    <style>
        body {{ margin: 0; padding: 0; }}
        #swagger-ui {{ max-width: 1460px; margin: 0 auto; }}
        .topbar {{ display: none; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
                plugins: [SwaggerUIBundle.plugins.DownloadUrl],
                layout: "StandaloneLayout",
                persistAuthorization: true
            }});
        }};
    </script>
</body>
</html>"""


def success_response(description="Success", example=None):
    """Standard success response schema"""
    schema = {
        "description": description,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                }
            }
        }
    }
    if example:
        schema["content"]["application/json"]["example"] = example
    return schema


def error_response(description="Error", example=None):
    """Standard error response schema"""
    schema = {
        "description": description,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"}
                    }
                }
            }
        }
    }
    if example:
        schema["content"]["application/json"]["example"] = example
    return schema


data_parser = DataParser()


api_router = APIRouter(
    title="Momo SMS Data API",
    version="1.0.0",
    description="API for SMS transaction data management and parsing"
)


@api_router.route(
    path="/",
    methods=["GET"],
    summary="Authentication check",
    description="Verify basic authentication credentials",
    require_auth=True,
    responses={
        "200": success_response("Authentication successful", {"message": "Authentication successful"}),
        "401": error_response("Unauthorized", {"error": "Unauthorized: Invalid or missing credentials"})
    },
    tags=["Authentication"]
)
def _doc_auth():
    pass


@api_router.route(
    path="/transactions",
    methods=["GET"],
    summary="Get all transactions",
    description="Retrieve all SMS transactions from the system",
    require_auth=True,
    responses={
        "200": {
            "description": "List of transactions",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "transaction_id": {"type": "integer"},
                                "sender": {"type": "string"},
                                "type": {"type": "string", "enum": ["received", "sent"]},
                                "amount_rwf": {"type": "number"},
                                "from": {"type": "string"},
                                "phone_masked": {"type": "string"},
                                "date": {"type": "string"},
                                "readable_date": {"type": "string"},
                                "balance_rwf": {"type": "number"}
                            }
                        }
                    },
                    "example": [
                        {
                            "transaction_id": 1,
                            "sender": "MTN",
                            "type": "received",
                            "amount_rwf": 5000,
                            "from": "John Doe",
                            "phone_masked": "*******123",
                            "date": "2026-01-24T10:30:00",
                            "readable_date": "24 Jan 2026 10:30:00 AM",
                            "balance_rwf": 5000
                        }
                    ]
                }
            }
        },
        "401": error_response("Unauthorized", {"error": "Unauthorized: Invalid or missing credentials"})
    },
    tags=["Transactions"]
)
def _doc_get_transactions():
    pass


@api_router.route(
    path="/transactions",
    methods=["POST"],
    summary="Create a new transaction",
    description="Create a new SMS transaction. Phone numbers are automatically masked for security.",
    require_auth=True,
    responses={
        "201": {
            "description": "Transaction created successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "message": {"type": "string"},
                            "data": {
                                "type": "object",
                                "properties": {
                                    "transaction_id": {"type": "integer"},
                                    "sender": {"type": "string"},
                                    "type": {"type": "string"},
                                    "amount_rwf": {"type": "number"},
                                    "from": {"type": "string"},
                                    "phone_masked": {"type": "string"},
                                    "date": {"type": "string"},
                                    "readable_date": {"type": "string"},
                                    "balance_rwf": {"type": "number"}
                                }
                            }
                        }
                    },
                    "example": {
                        "status": "success",
                        "message": "Transaction created successfully",
                        "data": {
                            "transaction_id": 2,
                            "sender": "MTN",
                            "type": "sent",
                            "amount_rwf": 1000,
                            "from": "Jane Doe",
                            "phone_masked": "*******456",
                            "date": "2026-01-24T11:00:00",
                            "readable_date": "24 Jan 2026 11:00:00 AM",
                            "balance_rwf": 4000
                        }
                    }
                }
            }
        },
        "400": error_response("Bad request - Validation error",
                              {"error": "Bad Request: Missing required fields (sender, type, amount_rwf, from, phone)"}),
        "401": error_response("Unauthorized", {"error": "Unauthorized: Invalid or missing credentials"}),
        "500": error_response("Internal server error", {"error": "Internal Server Error: Could not save transaction"})
    },
    tags=["Transactions"]
)
def _doc_create_transaction():
    pass


@api_router.route(
    path="/transactions/{id}",
    methods=["DELETE"],
    summary="Delete a transaction",
    description="Remove a transaction from the system by its transaction ID",
    require_auth=True,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
            "description": "Transaction ID to delete"
        }
    ],
    responses={
        "200": {
            "description": "Transaction deleted successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "message": {"type": "string"},
                            "transaction_id": {"type": "integer"}
                        }
                    },
                    "example": {
                        "status": "success",
                        "message": "Transaction deleted successfully",
                        "transaction_id": 1
                    }
                }
            }
        },
        "400": error_response("Bad request - Invalid ID format",
                              {"error": "Bad Request: Invalid transaction ID format"}),
        "401": error_response("Unauthorized", {"error": "Unauthorized: Invalid or missing credentials"}),
        "404": error_response("Not found", {"error": "Not Found: Transaction with ID 1 not found"}),
        "500": error_response("Internal server error", {"error": "Internal Server Error: Could not delete transaction"})
    },
    tags=["Transactions"]
)
def _doc_delete_transaction():
    pass


@api_router.route(
    path="/one-time-data-parser",
    methods=["POST"],
    summary="Parse XML data to JSON (One-time only)",
    description="Converts XML data from app/assets/modified_sms_v2.xml to JSON format and saves to assets/transactions.json. "
                "This endpoint can only be called once successfully. Subsequent calls will return an error.",
    require_auth=True,
    responses={
        "200": {
            "description": "Data parsed successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "message": {"type": "string"},
                            "data": {"type": "object"},
                            "record_count": {"type": "integer"},
                            "output_file": {"type": "string"}
                        }
                    },
                    "example": {
                        "success": True,
                        "message": "XML data successfully parsed to JSON and saved to transactions.json",
                        "data": {},
                        "record_count": 5,
                        "output_file": "/path/to/assets/transactions.json"
                    }
                }
            }
        },
        "400": error_response("Bad request - Already parsed or file error",
                              {"error": "Data has already been parsed. This endpoint can only be called once."}),
        "401": error_response("Unauthorized", {"error": "Unauthorized: Invalid or missing credentials"})
    },
    tags=["Data Management"]
)
def _doc_data_parser():
    pass


@api_router.route(
    path="/api-docs",
    methods=["GET"],
    summary="Swagger UI Documentation",
    description="Interactive Swagger UI interface to explore and test all available API endpoints",
    require_auth=False,
    responses={
        "200": {
            "description": "Swagger UI HTML page",
            "content": {"text/html": {"schema": {"type": "string"}}}
        }
    },
    tags=["Documentation"]
)
def _doc_swagger_ui():
    pass


@api_router.route(
    path="/openapi.json",
    methods=["GET"],
    summary="OpenAPI JSON Specification",
    description="Get the OpenAPI 3.0 JSON specification for all available endpoints. "
                "Automatically generated using apispec.",
    require_auth=False,
    responses={
        "200": {
            "description": "OpenAPI 3.0 specification",
            "content": {"application/json": {"schema": {"type": "object"}}}
        }
    },
    tags=["Documentation"]
)
def _doc_openapi_spec():
    pass


def handle_auth_check(handler):
    """Verify that the user has valid authentication credentials"""
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
    """Parse XML data from assets folder and convert to JSON format"""
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


def handle_swagger_ui(handler):
    """Serve Swagger UI interface for interactive API documentation"""
    html = api_router.get_swagger_ui_html()
    handler.send_response(200)
    handler.send_header('Content-type', 'text/html; charset=utf-8')
    handler.end_headers()
    handler.wfile.write(html.encode('utf-8'))


def handle_openapi_spec(handler):
    """Generate and serve OpenAPI specification using apispec"""
    spec = api_router.get_openapi_spec()
    handler.send_response(200)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(spec, indent=2).encode())


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
        "/transactions": get_transactions,
        "/api-docs": handle_swagger_ui,
        "/openapi.json": handle_openapi_spec,
    },
    "POST": {
        "/transactions": create_transaction,
        "/one-time-data-parser": handle_data_parser,
    },
    "DELETE": {
        "/transactions/:id": delete_transaction,
    }
}
