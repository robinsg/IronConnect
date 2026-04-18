from typing import Optional
from framework.core.terminal_driver import TmuxDriver
from framework.core.config import IBMiConfig
from framework.screens.login_screen import LoginScreen

class IBMiLibrary:
    """
    Robot Framework Library for IBM i (TN5250) automation.
    This library acts as a bridge between Robot Framework keywords and the Python POM framework.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.driver: Optional[TmuxDriver] = None
        self.current_screen = None

    def initialize_connection(self, host: Optional[str] = None, ssl: bool = False, device_name: Optional[str] = None):
        """
        Initialises the TN5250 connection via Tmux.
        
        Example:
        | Initialize Connection | host=pub400.com | ssl=${True} |
        """
        config = IBMiConfig.load()
        if host:
            config.host = host
        if ssl:
            config.ssl_enabled = ssl
        if device_name:
            config.device_name = device_name
            
        self.driver = TmuxDriver()
        self.driver.start_session(config=config)

    def login_to_system(self, user: str, password: str):
        """
        Performs a login using the LoginScreen POM.
        
        Example:
        | Login To System | user=MYUSER | password=MYPASS |
        """
        if not self.driver:
            raise RuntimeError("Driver not initialised. Call 'Initialize Connection' first.")
            
        login_screen = LoginScreen(self.driver)
        login_screen.login(user, password)
        self.current_screen = login_screen

    def verify_positional_text(self, text: str, row: int, col: int):
        """
        Verifies that specific text exists at the given row and column.
        
        Example:
        | Verify Positional Text | text=Sign On | row=1 | col=36 |
        """
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
            
        # We can use the current screen's verify logic or manual driver check
        # Here we demonstrate using a generic verify via a temporary screen or direct driver access
        # Best practice is to ensure the current screen is verified.
        if self.current_screen:
            # We can dynamically add an indicator to the current screen config for this check
            # but usually, Robot keywords are used for ad-hoc checks or assertions.
            buffer = self.driver.get_buffer()
            width, _ = self.driver.get_dimensions()
            
            target_row = int(row) - 1
            target_col = int(col) - 1
            
            if target_row >= len(buffer):
                raise AssertionError(f"Row {row} is out of bounds.")
                
            row_content = buffer[target_row].ljust(width)
            actual_text = row_content[target_col:target_col + len(text)]
            
            if actual_text != text:
                raise AssertionError(f"Positional mismatch at R{row}C{col}: Expected '{text}', found '{actual_text}'")

    def press_terminal_key(self, key: str):
        """
        Sends a control key to the terminal.
        
        Example:
        | Press Terminal Key | Enter |
        """
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
        self.driver.send_keys(key)

    def close_connection(self):
        """
        Closes the tmux session.
        """
        if self.driver and self.driver.session:
            self.driver.session.kill_session()
            self.driver = None
