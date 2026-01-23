"""
API Route and Documentation System using apispec
Framework-agnostic decorator-based routing with automatic OpenAPI generation
"""

from apispec import APISpec
from functools import wraps
import json

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
        
        # Add security scheme for Basic Auth
        self.spec.components.security_scheme(
            "basicAuth",
            {
                "type": "http",
                "scheme": "basic",
                "description": "Basic HTTP authentication"
            }
        )
        
        # Route registry: {method: {path: handler}}
        self.routes = {}
    
    def route(self, path, methods=None, summary="", description="", 
              require_auth=False, responses=None, tags=None):
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
            # Register route for each method
            for method in methods:
                method_upper = method.upper()
                if method_upper not in self.routes:
                    self.routes[method_upper] = {}
                self.routes[method_upper][path] = handler
            
            # Build OpenAPI operation
            operation = {
                "summary": summary or handler.__name__.replace("_", " ").title(),
                "description": description or handler.__doc__ or "",
                "responses": responses
            }
            
            if tags:
                operation["tags"] = tags
            
            if require_auth:
                operation["security"] = [{"basicAuth": []}]
                # Add 401 response if not present
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
            
            # Register with apispec for each method
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


# Common response schemas for reuse
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
