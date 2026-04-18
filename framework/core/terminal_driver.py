import time
import libtmux
from typing import List, Optional
from .exceptions import TerminalTimeoutError, ConnectionLostError
from .config import IBMiConfig

class TmuxDriver:
    """
    Handles the low-level interface between Python and the tn5250 binary running in tmux.
    """
    
    def __init__(self, session_name: str = "ibm_i_automation", socket_name: Optional[str] = None):
        self.server = libtmux.Server(socket_name=socket_name)
        self.session_name = session_name
        self.session = None
        self.window = None
        self.pane = None

    def start_session(self, config: Optional[IBMiConfig] = None):
        """
        Launches the tn5250 binary inside a new tmux session using the provided configuration.
        Defaults to language code 285 (UK English).
        """
        if config is None:
            config = IBMiConfig.load()

        if self.server.has_session(self.session_name):
            self.session = self.server.find_where({"session_name": self.session_name})
        else:
            # Construct the tn5250 command with all parameters
            # map=<map_code>
            # env.DEVNAME=<device_name>
            # env.TERM=<device_type>
            # +ssl or -ssl
            
            cmd_parts = ["tn5250"]
            
            # Application of the UK English map or custom map
            cmd_parts.append(f"map={config.map_code}")
            
            # SSL Configuration
            if config.ssl_enabled:
                cmd_parts.append("+ssl")
            
            # Device Name (DEVNAME)
            if config.device_name:
                cmd_parts.append(f"env.DEVNAME={config.device_name}")
            
            # Device Type (TERM)
            if config.device_type:
                cmd_parts.append(f"env.TERM={config.device_type}")
            
            # Destination Host
            cmd_parts.append(config.host)
            
            full_cmd = " ".join(cmd_parts)
            
            # Launch the session
            self.session = self.server.new_session(
                session_name=self.session_name, 
                window_command=full_cmd
            )
        
        self.window = self.session.attached_window
        self.pane = self.window.attached_pane

    def send_keys(self, keys: str, enter: bool = True):
        """Sends raw keys to the tmux pane."""
        self.pane.send_keys(keys, enter=enter)

    def get_buffer(self) -> List[str]:
        """Captures the current visual buffer of the tmux pane."""
        return self.pane.capture_pane()

    def wait_for_string(self, target: str, timeout: int = 10) -> bool:
        """Polls the buffer until a specific string appears or timeout is reached."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            buffer = self.get_buffer()
            if any(target in line for line in buffer):
                return True
            time.sleep(0.5)
        raise TerminalTimeoutError(f"String '{target}' not found within {timeout}s")

    def is_input_inhibited(self) -> bool:
        """
        Checks if 'Input Inhibited' status is present (usually at the bottom row).
        Implementation depends on specific tn5250 status line behavior.
        """
        buffer = self.get_buffer()
        # Typical indicator: "X" or "II" or "Input Inhibited" in the last line or status line
        # This is a representative check:
        status_line = buffer[-1] if buffer else ""
        return "X" in status_line or "Inhibited" in status_line
