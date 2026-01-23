from http.server import HTTPServer
from api.controller import SMSTransactionsController

if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SMSTransactionsController)
    print("Starting server on port 8000...")
    httpd.serve_forever()