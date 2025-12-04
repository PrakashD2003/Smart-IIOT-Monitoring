"""Custom exceptions and helpers for detailed error reporting."""

import logging
from types import TracebackType
from typing import Optional


def format_and_log_exception(
    exc: Exception, logger: Optional[logging.Logger] = None
) -> str:
    """
    Build a detailed error message including file, line, and original exception,
    then log it at ERROR level.
    """
    # Prefer the traceback attached to the exception object
    tb: Optional[TracebackType] = getattr(exc, "__traceback__", None)

    # If no traceback available, return a safe, logged message
    if tb is None:
        msg = f"Error: {exc} (no traceback available)"
        if logger:
            logger.error(msg)
        else:
            logging.error(msg)
        return msg

    # Now tb is not None (TracebackType). Walk to the innermost frame.
    while tb.tb_next is not None:
        tb = tb.tb_next

    frame = tb.tb_frame
    lineno = tb.tb_lineno

    if frame is None or lineno is None:
        msg = f"Error: {exc} (traceback incomplete)"
    else:
        filename = frame.f_code.co_filename
        msg = f"Error in {filename}, line {lineno}: {exc}"

    if logger:
        logger.error(msg)
    else:
        logging.error(msg)

    return msg


class DetailedException(Exception):
    """
    Exception that automatically formats and logs its own traceback location.
    """

    def __init__(self, exc: Exception, logger: Optional[logging.Logger] = None) -> None:
        """
        Wraps an existing exception, logs file/line context, and carries
        a detailed message forward.

        :param exc: The original exception to wrap.
        :param logger: Optional logger for error output.
        """
        # Format and log
        detailed_msg = format_and_log_exception(exc, logger)
        # Initialize base with the detailed message
        super().__init__(detailed_msg)
