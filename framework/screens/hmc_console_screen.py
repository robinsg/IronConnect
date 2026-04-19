import time
from framework.core.base_screen import BaseScreen
from framework.core.terminal_driver import TmuxDriver
from framework.core.config import IBMiConfig

class HMCConsoleScreen(BaseScreen):
    """
    Handles navigation through the HMC command-line / character-based interface
    to establish a system console session.
    """
    
    def __init__(self, driver: TmuxDriver):
        # We point to the HMC config file
        super().__init__(driver, "framework/config/hmc_screens.yaml")

    def establish_console(self, config: IBMiConfig):
        """
        Orchestrates the navigation from HMC Login to the IBM i Sign On screen.
        """
        # 1. HMC Login
        # Note: In a multi-screen YAML, we might need a way to switch context 
        # or just use the indicators to verify the state.
        # Since BaseScreen loads the whole dict, we should probably modify it
        # or just use specific keys here.
        
        # Step: Login
        self.driver.wait_for_string("Login:", timeout=20)
        self.driver.send_keys(config.hmc_user, enter=True)
        self.driver.wait_for_string("Password:", timeout=5)
        self.driver.send_keys(config.hmc_password, enter=True)

        # Step: Language selection (if prompted)
        # Often HMC asks for language if not default
        # user specified HMC language defaults to 23
        
        # Step: Navigate menus to find Managed System and LPAR
        # This part varies by HMC version, but usually involves selecting numbers
        # For simplicity in this architectural demo, we simulate the selection sequence:
        
        # 1. Select 'Managed Systems'
        self.driver.wait_for_string("Managed Systems", timeout=15)
        self.driver.send_keys("1") # Simulate selection
        
        # 2. Select the specific Power System
        self.driver.wait_for_string(config.power_system, timeout=10)
        # Find index of power_system in buffer and send that number...
        # For now, we assume user knows the sequence or we search the buffer
        self._select_by_text(config.power_system)

        # 3. Select the Partition/LPAR
        self.driver.wait_for_string(config.lpar_name, timeout=10)
        self._select_by_text(config.lpar_name)

        # 4. Select Console Mode
        # 1=Dedicated, 2=Shared
        self.driver.wait_for_string("Terminal", timeout=10)
        self.driver.send_keys(config.console_mode)

        # 5. Handle Shared Console Password
        if config.console_mode == "2" and config.console_password:
            self.driver.wait_for_string("Password", timeout=5)
            self.driver.send_keys(config.console_password)

        print(f"HMC Console session established for {config.lpar_name}. Waiting for IBM i Sign On...")
        
        # Now we wait for the IBM i Sign On screen to appear on the console
        self.driver.wait_for_string("Sign On", timeout=60)

    def _select_by_text(self, text: str):
        """Helper to find a menu item number by its label text and select it."""
        buffer = self.driver.get_buffer()
        for i, line in enumerate(buffer):
            if text in line:
                # Often lines look like " 1. SYSTEM_NAME "
                parts = line.strip().split('.')
                if parts[0].isdigit():
                    self.driver.send_keys(parts[0])
                    return
        raise RuntimeError(f"Could not find menu item '{text}' in HMC buffer")
