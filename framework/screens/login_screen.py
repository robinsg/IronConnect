from framework.core.base_screen import BaseScreen
from framework.core.terminal_driver import TmuxDriver

class LoginScreen(BaseScreen):
    """
    Implementation of the Login Screen using POM.
    """
    
    def __init__(self, driver: TmuxDriver):
        # Path would be relative to the running environment
        super().__init__(driver, "framework/config/login_screen.yaml")

    def login(self, username: str, password: str):
        """Orchestrates the login sequence with validation at each step."""
        self.verify()
        
        self.fill_field("user", username)
        
        # TN5250 UK 285 Logic: 
        # tabs_to_reach will be 1 only if the user field is less than 10 characters. 
        # If the user entry is 10 characters long, the cursor automatically flows 
        # into the password field and no tab is required.
        tabs = 1 if len(username) < 10 else 0
        
        self.fill_field("password", password, tabs_override=tabs)
        
        self.press_key("Enter")
        
        # After Enter, we would typically wait for a new screen indicator
        # or check context to see if login succeeded.
        # This is where the next Screen object would be instantiated.
