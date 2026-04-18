import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class IBMiConfig:
    """
    Configuration for IBM i connectivity.
    Loads values from environment variables to ensure secrets are not hardcoded or committed to Git.
    """
    host: str = os.getenv("IBMI_HOST", "pub400.com")
    user: str = os.getenv("IBMI_USER", "")
    password: str = os.getenv("IBMI_PASSWORD", "")
    ssl_enabled: bool = os.getenv("IBMI_SSL", "false").lower() == "true"
    device_name: Optional[str] = os.getenv("IBMI_DEVICE_NAME")
    device_type: str = os.getenv("IBMI_DEVICE_TYPE", "IBM-3477-FC")
    map_code: str = os.getenv("IBMI_MAP", "285")

    @classmethod
    def load(cls) -> "IBMiConfig":
        """Factory method to load the configuration from the environment."""
        return cls()
