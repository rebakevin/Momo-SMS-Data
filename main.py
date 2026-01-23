from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
from api.auth import is_authenticated
from api.data_parser import DataParser
from api.router import APIRouter, success_response, error_response

# Initialize API Router with apispec
router = APIRouter(
    title="Momo SMS Data API",
    version="1.0.0",
    description="API for SMS transaction data management and parsing"
)

class SMSTransactionsHandler(BaseHTTPRequestHandler):
    
    # Initialize data parser instance
    data_parser = DataParser()
    
    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')

        if status_code == 401:
            self.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        
        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())
    
    def _send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _send_html_response(self, html, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path in router.routes.get('GET', {}):
            handler = router.routes['GET'][path]
            handler(self)
        else:
            self._send_error_response(404, "Route not found")
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path in router.routes.get('POST', {}):
            handler = router.routes['POST'][path]
            handler(self)
        else:
            self._send_error_response(404, "Route not found")
    
    # ========== Route Handlers ==========
    
    @router.route(
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
    def handle_auth_check(self):
        """Verify that the user has valid authentication credentials"""
        if not is_authenticated(self.headers):
            self._send_error_response(401, "Unauthorized: Invalid or missing credentials")
            return
        
        self._send_json_response({"message": "Authentication successful"})
    
    @router.route(
        path="/one-time-data-parser",
        methods=["POST"],
        summary="Parse XML data to JSON (One-time only)",
        description="Converts XML data from app/assets/modified_sms_v2.xml to JSON format. "
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
                                "record_count": {"type": "integer"}
                            }
                        },
                        "example": {
                            "success": True,
                            "message": "XML data successfully parsed to JSON",
                            "data": {},
                            "record_count": 5
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
    def handle_data_parser(self):
        """Parse XML data from assets folder and convert to JSON format"""
        if not is_authenticated(self.headers):
            self._send_error_response(401, "Unauthorized: Invalid or missing credentials")
            return
        
        try:
            result = self.data_parser.parse_xml_to_json()
            self._send_json_response(result)
        except Exception as e:
            self._send_error_response(400, str(e))
    
    @router.route(
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
    def handle_swagger_ui(self):
        """Serve Swagger UI interface for interactive API documentation"""
        html = router.get_swagger_ui_html()
        self._send_html_response(html)
    
    @router.route(
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
    def handle_openapi_spec(self):
        """Generate and serve OpenAPI specification using apispec"""
        spec = router.get_openapi_spec()
        self._send_json_response(spec)


if __name__ == "__main__":
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, SMSTransactionsHandler)
    print(f"Server running on http://localhost:{port}")
    print(f"API Documentation: http://localhost:{port}/api-docs")
    print(f"OpenAPI Spec: http://localhost:{port}/openapi.json")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()