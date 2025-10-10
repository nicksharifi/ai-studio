import logging
import functools

# Setup basic logging configuration
# logging.basicConfig(level=logging.INFO)


def log_inputs(func):
    @functools.wraps(func)  # This preserves the name and docstring of the original function
    def wrapper(*args, **kwargs):
        # Log the function name and its arguments
        logging.info(f"Called function: {func.__name__} with args: {args} and kwargs: {kwargs}")

        # Call the actual function
        return func(*args, **kwargs)

    return wrapper
