import base64

USERNAME = "admin"
PASSWORD = "admin"

def is_authenticated(headers):
    # Checking the request headers for valid Basic Authentication
    auth_header = headers.get("Authorization")

    if not auth_header:
        return False
    
    try:
        auth_type, encoded_credentials = auth_header.split(" ")
        
        if auth_type.lower() != "basic":
            return False
        
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')

        return username == USERNAME and password == PASSWORD
    except Exception:
        return False
