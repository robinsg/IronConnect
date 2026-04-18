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
        Configures terminal dimensions based on the device type.
        """
        if config is None:
            config = IBMiConfig.load()

        if self.server.has_session(self.session_name):
            self.session = self.server.find_where({"session_name": self.session_name})
        else:
            # Determine dimensions based on device type
            # 3477-FC is common for 27x132 support
            width, height = 80, 24
            if "3477" in config.device_type:
                width, height = 132, 27
            
            cmd_parts = ["tn5250"]
            cmd_parts.append(f"map={config.map_code}")
            
            if config.ssl_enabled:
                cmd_parts.append("+ssl")
            
            if config.device_name:
                cmd_parts.append(f"env.DEVNAME={config.device_name}")
            
            if config.device_type:
                cmd_parts.append(f"env.TERM={config.device_type}")
            
            cmd_parts.append(config.host)
            
            full_cmd = " ".join(cmd_parts)
            
            # Launch the session with explicit window dimensions
            self.session = self.server.new_session(
                session_name=self.session_name, 
                window_command=full_cmd,
                x=width,
                y=height
            )
        
        self.window = self.session.attached_window
        self.pane = self.window.attached_pane

    def get_dimensions(self) -> tuple[int, int]:
        """Returns the current pane dimensions (width, height)."""
        if not self.pane:
            return 80, 24
        return int(self.pane.display_width), int(self.pane.display_height)

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
