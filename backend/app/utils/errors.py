"""
Error handling utilities and decorators
Provides consistent error response format across all API endpoints
"""

from functools import wraps
from flask import jsonify, request
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error - bad request"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, details)


class NotFoundError(APIError):
    """Resource not found"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 404, details)


class InternalError(APIError):
    """Internal server error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 500, details)


def error_response(message: str, status_code: int = 400, details: dict = None) -> tuple:
    """
    Generate standardized error response
    
    Returns:
        (dict, int) - JSON response and HTTP status code
    """
    return jsonify({
        'status': 'error',
        'error': message,
        'details': details or {}
    }), status_code


def success_response(data=None, message: str = None, status_code: int = 200) -> tuple:
    """
    Generate standardized success response
    
    Returns:
        (dict, int) - JSON response and HTTP status code
    """
    response = {
        'status': 'success',
        'data': data
    }
    if message:
        response['message'] = message
    
    return jsonify(response), status_code


def validate_request(*required_fields):
    """
    Decorator to validate required JSON fields in request body
    
    Usage:
        @validate_request('market_ids', 'days')
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return error_response(
                        'Request body must be valid JSON',
                        400,
                        {'expected_fields': list(required_fields)}
                    )
                
                missing_fields = [
                    field for field in required_fields 
                    if field not in data
                ]
                
                if missing_fields:
                    return error_response(
                        'Missing required fields',
                        400,
                        {'missing': missing_fields}
                    )
                
            except Exception as e:
                logger.error(f"Request validation error: {str(e)}")
                return error_response('Invalid request', 400)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(**param_validators):
    """
    Decorator to validate query parameters
    
    param_validators: dict mapping param_name to (type, required, default)
    
    Usage:
        @validate_query_params(
            days=(int, False, 30),
            metric=(str, True, None)
        )
        def my_endpoint():
            days = request.args.get('days')
            metric = request.args.get('metric')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                for param_name, (param_type, required, default) in param_validators.items():
                    value = request.args.get(param_name)
                    
                    if value is None:
                        if required:
                            return error_response(
                                f'Missing required query parameter: {param_name}',
                                400,
                                {'param': param_name}
                            )
                        request.args = request.args.copy()
                        if default is not None:
                            request.args[param_name] = default
                    else:
                        # Type conversion and validation
                        try:
                            if param_type == int:
                                request.args = request.args.copy()
                                request.args[param_name] = int(value)
                            elif param_type == float:
                                request.args = request.args.copy()
                                request.args[param_name] = float(value)
                        except (ValueError, TypeError):
                            return error_response(
                                f'Invalid type for parameter {param_name}: expected {param_type.__name__}',
                                400,
                                {'param': param_name, 'expected_type': param_type.__name__}
                            )
                
            except Exception as e:
                logger.error(f"Query parameter validation error: {str(e)}")
                return error_response('Invalid query parameters', 400)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def handle_errors(f):
    """
    Decorator to catch and handle APIError exceptions
    
    Usage:
        @handle_errors
        def my_endpoint():
            raise ValidationError('Something is wrong')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API Error: {e.message}")
            return error_response(e.message, e.status_code, e.details)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return error_response(
                'Internal server error',
                500,
                {'error': str(e) if not isinstance(str(e), str) else 'Unknown error'}
            )
    
    return decorated_function
