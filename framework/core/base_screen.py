from typing import Dict, Any, List
import yaml
from .terminal_driver import TmuxDriver
from .exceptions import ScreenMismatchError, InputInhibitedError

class BaseScreen:
    """
    Base class for all screen objects. Implements the Screen State Machine.
    """
    
    def __init__(self, driver: TmuxDriver, config_path: str):
        self.driver = driver
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.screen_name = self.config.get('screen_name')
        self.indicators = self.config.get('indicators', [])
        self.fields = self.config.get('fields', {})

    def verify(self):
        """Mandatory check: Ensures the current screen buffer matches the expected YAML definition."""
        buffer = self.driver.get_buffer()
        buffer_text = "\n".join(buffer)
        
        for indicator in self.indicators:
            if indicator not in buffer_text:
                raise ScreenMismatchError(
                    f"Expected indicator '{indicator}' not found for screen '{self.screen_name}'"
                )
        
        if self.driver.is_input_inhibited():
            raise InputInhibitedError(f"Terminal is in inhibited state on screen '{self.screen_name}'")

    def fill_field(self, field_name: str, value: str, tabs_override: Optional[int] = None):
        """Fills a field based on its YAML definition (TAB management)."""
        if field_name not in self.fields:
            raise KeyError(f"Field '{field_name}' not defined in {self.screen_name} config")
        
        field_cfg = self.fields[field_name]
        # In this implementation, we assume we use Tab to navigate to fields
        # Real-world logic might include 'order' or 'tabs_to_reach' in YAML
        tabs = tabs_override if tabs_override is not None else field_cfg.get('tabs_to_reach', 0)
        for _ in range(tabs):
            self.driver.send_keys("Tab", enter=False)
            
        self.driver.send_keys(value, enter=False)

    def press_key(self, key: str):
        """Sends a specific control key (Enter, F3, etc.)."""
        self.driver.send_keys(key)
