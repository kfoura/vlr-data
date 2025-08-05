from functools import wraps

def enforce_types(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        hints = func.__annotations__
        for arg_name, arg_type in hints.items():
            if arg_name == "return":
                continue
            val = kwargs.get(arg_name, None)
            if val is None:
                arg_index = list(func.__code__.co_varnames).index(arg_name)
                if arg_index < len(args):
                    val = args[arg_index]
            if not isinstance(val, arg_type):
                raise TypeError(f"Argument '{arg_name}' must be {arg_type.__name__}, got {type(val).__name__}")
        return func(*args, **kwargs)
    return wrapper