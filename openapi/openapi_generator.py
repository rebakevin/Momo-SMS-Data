"""
OpenAPI Documentation Generator
Automatically generates OpenAPI specification from route handlers
"""

import json
from functools import wraps

class OpenAPIGenerator:
    def __init__(self, title, version, description):
        self.title = title
        self.version = version
        self.description = description
        self.routes = {}
        self.components = {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic"
                }
            }
        }
    
    def route(self, path, method="get", require_auth=False, summary=None, description=None, 
              responses=None, request_body=None, tags=None):
        """
        Decorator to register a route and its documentation
        
        Args:
            path: API endpoint path
            method: HTTP method (get, post, put, delete, etc.)
            require_auth: Whether the endpoint requires authentication
            summary: Short summary of the endpoint
            description: Detailed description
            responses: Dictionary of response codes and their schemas
            request_body: Request body schema
            tags: List of tags for grouping
        """
        def decorator(func):
            if path not in self.routes:
                self.routes[path] = {}
            
            # Build the operation spec
            operation = {
                "summary": summary or func.__name__.replace("_", " ").title(),
                "description": description or func.__doc__ or "",
                "operationId": f"{method}_{path.replace('/', '_').strip('_')}"
            }
            
            if tags:
                operation["tags"] = tags
            
            if require_auth:
                operation["security"] = [{"basicAuth": []}]
            
            if responses:
                operation["responses"] = responses
            else:
                operation["responses"] = {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            
            if request_body:
                operation["requestBody"] = request_body
            
            self.routes[path][method.lower()] = operation
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def generate_spec(self, server_url="http://localhost:8000"):
        """Generate the complete OpenAPI specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "servers": [
                {
                    "url": server_url,
                    "description": "Development server"
                }
            ],
            "components": self.components,
            "paths": self.routes
        }
        return spec
    
    def get_spec_json(self, server_url="http://localhost:8000", indent=2):
        """Get the OpenAPI spec as JSON string"""
        return json.dumps(self.generate_spec(server_url), indent=indent)
    
    def get_swagger_ui_html(self, openapi_json_url="/openapi.json", page_title=None):
        """
        Generate Swagger UI HTML page
        
        Args:
            openapi_json_url: URL to the OpenAPI JSON specification endpoint
            page_title: Custom page title (defaults to API title)
        
        Returns:
            HTML string for Swagger UI
        """
        title = page_title or f"{self.title} - Documentation"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui.css" />
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        #swagger-ui {{
            max-width: 1460px;
            margin: 0 auto;
        }}
        .topbar {{
            display: none;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '{openapi_json_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                persistAuthorization: true,
                tryItOutEnabled: true
            }});
            window.ui = ui;
        }};
    </script>
</body>
</html>"""
        return html


# Response schema templates
class ResponseSchemas:
    """Common response schema templates"""
    
    @staticmethod
    def success_message(example_message="Operation successful"):
        return {
            "200": {
                "description": "Success",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "example": example_message
                                }
                            }
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def error_response(code, message):
        return {
            str(code): {
                "description": message,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string",
                                    "example": message
                                }
                            }
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def combined_responses(*response_dicts):
        """Combine multiple response dictionaries"""
        result = {}
        for resp_dict in response_dicts:
            result.update(resp_dict)
        return result
    
    @staticmethod
    def unauthorized():
        return ResponseSchemas.error_response(
            401, 
            "Unauthorized: Invalid or missing credentials"
        )
    
    @staticmethod
    def bad_request(message="Bad request"):
        return ResponseSchemas.error_response(400, message)
    
    @staticmethod
    def not_found(message="Resource not found"):
        return ResponseSchemas.error_response(404, message)
