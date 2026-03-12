import base64

USERNAME = "admin"
PASSWORD = "admin"

def is_authenticated(headers):

    auth_header = headers.get("Authorization")

    if not auth_header:
        return False, None
    
    try:
        auth_type, encoded_credentials = auth_header.split(" ")
        
        if auth_type.lower() != "basic":
            return False, None
        
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')

        if username == USERNAME and password == PASSWORD:
            return True, 1 
            
        return False, None
    except Exception:
        return False, None
