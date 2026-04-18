from typing import Dict, Any, List, Optional
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
        """
        Mandatory check: Ensures the current screen buffer matches the expected YAML definition.
        Supports both global string indicators and positional (row/col) indicators.
        """
        buffer = self.driver.get_buffer()
        buffer_text = "\n".join(buffer)
        
        for indicator in self.indicators:
            if isinstance(indicator, str):
                # Standard global string check (anywhere on screen)
                if indicator not in buffer_text:
                    raise ScreenMismatchError(
                        f"Expected global indicator '{indicator}' not found for screen '{self.screen_name}'"
                    )
            elif isinstance(indicator, dict):
                # Positional check: text at specific row and col (1-indexed for YAML clarity)
                text = indicator.get('text', '')
                try:
                    row = int(indicator.get('row', 0))
                    col = int(indicator.get('col', 0))
                except (ValueError, TypeError):
                    continue

                if not text or row <= 0 or col <= 0:
                    continue 

                # Buffer access (0-indexed)
                target_row = row - 1
                target_col = col - 1

                if target_row >= len(buffer):
                    raise ScreenMismatchError(f"Row {row} is out of bounds for the current buffer.")

                # Dynamic width padding based on driver dimensions
                width, _ = self.driver.get_dimensions()
                row_content = buffer[target_row].ljust(width) 
                actual_text = row_content[target_col:target_col + len(text)]

                if actual_text != text:
                    raise ScreenMismatchError(
                        f"Positional mismatch at R{row}C{col}: Expected '{text}', found '{actual_text}'"
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
