from functools import wraps
from inspect import signature

def enforce_types(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        hints = func.__annotations__
        
        for arg_name, arg_type in hints.items():
            if arg_name == "return":
                continue
            val = bound_args.arguments.get(arg_name)
            if not isinstance(val, arg_type):
                raise TypeError(f"Argument '{arg_name}' must be {arg_type.__name__}, got {type(val).__name__}")
        return func(*args, **kwargs)
    return wrapper

class InvalidContentTypeException(Exception):
    '''Raised when response content type is not text/html'''
    pass

class InvalidPlayerException(Exception):
    '''Raised when player id or player does not exist'''
    pass

class NoNameException(Exception):
    '''Raised when a player page has no name associated with it'''
    pass