import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class IBMiConfig:
    """
    Configuration for IBM i connectivity.
    Loads values from environment variables to ensure secrets are not hardcoded or committed to Git.
    """
    # Direct / LPAR Connection
    host: str = os.getenv("IBMI_HOST", "pub400.com")
    user: str = os.getenv("IBMI_USER", "")
    password: str = os.getenv("IBMI_PASSWORD", "")
    ssl_enabled: bool = os.getenv("IBMI_SSL", "false").lower() == "true"
    device_name: Optional[str] = os.getenv("IBMI_DEVICE_NAME")
    device_type: str = os.getenv("IBMI_DEVICE_TYPE", "IBM-3477-FC")
    map_code: str = os.getenv("IBMI_MAP", "285")

    # HMC Console Connection
    hmc_host: Optional[str] = os.getenv("HMC_HOST")
    hmc_user: Optional[str] = os.getenv("HMC_USER")
    hmc_password: Optional[str] = os.getenv("HMC_PASSWORD")
    hmc_language: str = os.getenv("HMC_LANGUAGE", "23")
    power_system: Optional[str] = os.getenv("POWER_SYSTEM")
    lpar_name: Optional[str] = os.getenv("LPAR_NAME")
    console_mode: str = os.getenv("CONSOLE_MODE", "2")  # 1=Dedicated, 2=Shared
    console_password: Optional[str] = os.getenv("CONSOLE_PASSWORD")

    # Connection Strategy
    connection_mode: str = os.getenv("IBMI_CONNECTION_MODE", "direct") # 'direct' or 'console'

    @classmethod
    def load(cls) -> "IBMiConfig":
        """Factory method to load the configuration from the environment."""
        return cls()
