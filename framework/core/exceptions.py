class TerminalError(Exception):
    """Base exception for all terminal-related errors."""
    pass

class TerminalTimeoutError(TerminalError):
    """Raised when a terminal operation times out."""
    pass

class ScreenMismatchError(TerminalError):
    """Raised when the current screen does not match the expected screen definition."""
    pass

class ConnectionLostError(TerminalError):
    """Raised when the connection to the TN5250 server is lost."""
    pass

class InputInhibitedError(TerminalError):
    """Raised when input is sent while the terminal is inhibited."""
    pass
