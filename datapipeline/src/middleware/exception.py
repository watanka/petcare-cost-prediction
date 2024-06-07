from traceback import print_exception

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except Exception as e:
            print_exception(e)
            return JSONResponse(
                status_code=e.status_code if hasattr(e,'status_code') else 500,
                content={
                    'error': e.__class__.__name__, 
                    'messages': "server side error"
                }
            )
            

class BreedInfoNotFoundError(Exception):
    
    def __init__(self, message, errors = None):
        super().__init__(message)
        self.errors = errors
        