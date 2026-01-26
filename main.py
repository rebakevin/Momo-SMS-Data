from http.server import HTTPServer
from api.controller import SMSTransactionsController

if __name__ == "__main__":
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, SMSTransactionsController)
    print(f"Starting server on port {port}...")
    print(f"API Documentation: http://localhost:{port}/api-docs")
    print(f"OpenAPI Spec: http://localhost:{port}/openapi.json")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()