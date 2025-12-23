from ninja_extra import api_controller, route
from ninja_extra.permissions import AllowAny
from ninja import Schema
from typing import Dict, Any

# Simple schema for response
class HelloResponse(Schema):
    message: str
    status: str = "success"
    timestamp: str

@api_controller('/test', tags=['Test'], permissions=[AllowAny])
class TestController:
    """Simple test API endpoints"""
    
    @route.get('/hello', response=HelloResponse)
    def hello_world(self):
        """Simple Hello World endpoint"""
        from datetime import datetime
        return {
            "message": "Hello World! API is working!",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    
    @route.get('/ping', response=Dict[str, str])
    def ping(self):
        """Simple ping endpoint"""
        return {"ping": "pong"}
    
    @route.get('/echo/{text}', response=Dict[str, Any])
    def echo(self, text: str):
        """Echo back the input text"""
        return {
            "original": text,
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "length": len(text),
            "reversed": text[::-1]
        }