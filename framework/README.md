# IronConnect: IBM i Automation Framework

## Overview
IronConnect is a robust, enterprise-grade automation framework designed for IBM i (TN5250) systems. It utilises a decoupled architecture where screen definitions are managed via YAML, and interactions are handled through a persistent tmux session managed by Python. All sessions are configured by default to use language code **285 (UK English)**.

## Core Components
- **`TmuxDriver`**: Interfaces with `libtmux` to send keys and capture buffers.
- **`BaseScreen`**: Implements the State Machine, ensuring "Input Inhibited" and indicator checks occur before every action.
- **`IBMiLibrary`**: A Robot Framework bridge that exposes Python POM logic as natural language keywords.
- **`YAML Configs`**: Store screen identifiers and field mappings, removing coordinates from code.
- **`Page Object Model (POM)`**: Encapsulates screen-specific logic into reusable classes.

## Getting Started (Local Environment)

### Prerequisites
1.  **TN5250 Binary**: Ensure `tn5250` is installed and in your PATH.
    - Linux: `sudo apt install tn5250`
    - macOS: `brew install tn5250`
2.  **Tmux**: `sudo apt install tmux`
3.  **Python 3.12+**

### Installation
```bash
pip install libtmux pyyaml
```

### Running Automation
```python
from framework.core.terminal_driver import TmuxDriver
from framework.screens.login_screen import LoginScreen

# Initialise Driver (automatically loads config from environment)
driver = TmuxDriver()
driver.start_session() 

# POM Interaction
login = LoginScreen(driver)
login.login("USERNAME", "PASSWORD")
```

### Orchestration with Robot Framework
For enterprise-grade orchestration and reporting, utilise the built-in Robot Framework library.

**Example Test Case (`tasks/login_tests.robot`):**
```robot
*** Settings ***
Library    framework.libraries.IBMiLibrary

*** Test Cases ***
Authenticate To LPAR
    Initialize Connection
    Login To System    user=MYUSER    password=MYPASS
    Verify Positional Text    text=MAIN MENU    row=1    col=35
    [Teardown]    Close Connection
```

**Execution:**
```bash
robot tasks/login_tests.robot
```

### Multi-System Orchestration
When managing multiple IBM i instances, use the `run_tasks.py` orchestrator. This script automatically organises results into system-specific folders with timestamps.

**Execution:**
```bash
# results/pub400_com/20240418_1325/
IBMI_HOST=pub400.com python3 run_tasks.py tasks/login_tests.robot
```

The orchestrator also embeds a real-time terminal buffer capture directly into the Robot Framework `log.html` upon any verification failure, providing instant visual debugging for remote LPARs.

## Connectivity Configuration
IronConnect supports both direct IP connectivity to LPARs and advanced **System Console** sessions via a Hardware Management Console (HMC).

### Direct Mode (Default)
Standard 5250 connection directly to the IBM i host.

### Console Mode (HMC)
For monitoring IPLs or system maintenance, the framework can pivot through an HMC to establish a console session on port 2301 via SSL.

**Environment Variables for HMC:**
```env
IBMI_CONNECTION_MODE=console
HMC_HOST=hmc.yourdomain.com
HMC_USER=hmcuser
HMC_PASSWORD=hmcpass
HMC_LANGUAGE=23
POWER_SYSTEM=SystemA
LPAR_NAME=LPAR01
CONSOLE_MODE=2        # 1=Dedicated, 2=Shared
CONSOLE_PASSWORD=     # Required if Shared
```

**Robot Keyword Usage:**
```robot
*** Test Cases ***
IPL Monitoring Task
    Initialize Connection    connection_mode=console
    Login To System          user=QSECOFR    password=PASSWORD
```

### Scalable Data-Driven Automation
To avoid a massive number of Python classes, the framework supports **Generic Dynamic Screens**. You can define dozens of screens in an external YAML file and automate them using a single keyword.

**Example Dynamic Worklfow (`tasks/custom_tests.robot`):**
```robot
*** Test Cases ***
Verify Inventory System
    Initialize Connection
    # No Python class needed for these screens:
    Verify and Interact With Screen    config_path=framework/config/inventory.yaml    screen_key=main_menu     data=${selection_data}
    Verify and Interact With Screen    config_path=framework/config/inventory.yaml    screen_key=part_lookup    data=${part_id_data}
    [Teardown]    Close Connection
```

This approach allows you to scale to 30+ screens per system with zero additional code—simply update your YAML definitions.

## Security & Stability
- **Mandatory Validation**: Every navigation is verified against YAML indicators.
- **Exception Handling**: Custom hierarchy for `TerminalTimeoutError`, `ScreenMismatchError`, etc.
- **Wait States**: Intelligent polling of the "Input Inhibited" flag to prevent dropped keystrokes.
