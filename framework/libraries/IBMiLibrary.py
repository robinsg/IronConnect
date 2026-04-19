from typing import Optional
from robot.api import logger
from framework.core.terminal_driver import TmuxDriver
from framework.core.config import IBMiConfig
from framework.screens.login_screen import LoginScreen
from framework.screens.hmc_console_screen import HMCConsoleScreen

class IBMiLibrary:
    """
    Robot Framework Library for IBM i (TN5250) automation.
    This library acts as a bridge between Robot Framework keywords and the Python POM framework.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.driver: Optional[TmuxDriver] = None
        self.current_screen = None
        self.config: Optional[IBMiConfig] = None

    def initialize_connection(self, host: Optional[str] = None, ssl: bool = False, connection_mode: str = "direct"):
        """
        Initialises the TN5250 connection via Tmux.
        Supports 'direct' and 'console' modes.
        
        Example:
        | Initialize Connection | connection_mode=console |
        """
        self.config = IBMiConfig.load()
        if host:
            self.config.host = host
        if ssl:
            self.config.ssl_enabled = ssl
        
        self.config.connection_mode = connection_mode
            
        self.driver = TmuxDriver()
        
        # When in console mode, we connect to HMC target on port 2301
        # We need to temporarily override host/ssl for the driver if it's console mode
        if connection_mode == "console":
            if not self.config.hmc_host:
                raise ValueError("HMC_HOST must be set for console connection mode")
            
            # HMC always requires SSL on port 2301
            # We modify the config object passed to the driver start_session
            console_cfg = IBMiConfig.load()
            console_cfg.host = f"{self.config.hmc_host}:2301"
            console_cfg.ssl_enabled = True
            self.driver.start_session(config=console_cfg)
        else:
            self.driver.start_session(config=self.config)

    def login_to_system(self, user: Optional[str] = None, password: Optional[str] = None):
        """
        Performs a login. If connection_mode is 'console', it first navigates 
        through the HMC menus to establish the console session.
        """
        if not self.driver or not self.config:
            raise RuntimeError("Driver not initialised. Call 'Initialize Connection' first.")

        # 1. Handle HMC navigation if necessary
        if self.config.connection_mode == "console":
            hmc = HMCConsoleScreen(self.driver)
            hmc.establish_console(self.config)

        # 2. Proceed with standard IBM i login
        login_screen = LoginScreen(self.driver)
        # Use provided credentials or fall back to config
        u = user if user else self.config.user
        p = password if password else self.config.password
        
        login_screen.login(u, p)
        self.current_screen = login_screen

    def verify_positional_text(self, text: str, row: int, col: int):
        """
        Verifies that specific text exists at the given row and column.
        
        Example:
        | Verify Positional Text | text=Sign On | row=1 | col=36 |
        """
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
            
        buffer = self.driver.get_buffer()
        width, _ = self.driver.get_dimensions()
        
        target_row = int(row) - 1
        target_col = int(col) - 1
        
        if target_row >= len(buffer):
            msg = f"Row {row} is out of bounds."
            self.capture_screen_to_log(label=f"FAILURE: {msg}")
            raise AssertionError(msg)
            
        row_content = buffer[target_row].ljust(width)
        actual_text = row_content[target_col:target_col + len(text)]
        
        if actual_text != text:
            msg = f"Positional mismatch at R{row}C{col}: Expected '{text}', found '{actual_text}'"
            self.capture_screen_to_log(label=f"FAILURE: {msg}")
            raise AssertionError(msg)

    def capture_screen_to_log(self, label: str = "Terminal Buffer Capture"):
        """
        Captures the current tmux buffer and embeds it in the Robot Framework log.
        """
        if self.driver:
            buffer = self.driver.get_buffer()
            screen_text = "\n".join(buffer)
            logger.info(f"<div style='background-color:black; color:#00FF41; padding:10px; font-family:monospace; white-space:pre;'><b>{label}</b><br>{screen_text}</div>", html=True)

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
