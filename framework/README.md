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
IronConnect supports connectivity to diverse IBM i hosts (including local LPARs and on-site servers) via environment variables. This ensures that sensitive credentials are never hardcoded or committed to version control.

### Environment Specification (.env)
Create a `.env` file in the project root (following the template in `.env.example`):

```env
IBMI_HOST=your.host.name
IBMI_USER=your_username
IBMI_PASSWORD=your_password
IBMI_SSL=true
IBMI_DEVICE_NAME=MYDEV01
IBMI_DEVICE_TYPE=IBM-3477-FC  # Supports 27x132 dimensions
IBMI_MAP=285
```

The framework prioritises these variables during the initialisation sequence and automatically resizes the underlying tmux window to 132x27 if a 3477-class device is selected.

## Security & Stability
- **Mandatory Validation**: Every navigation is verified against YAML indicators.
- **Exception Handling**: Custom hierarchy for `TerminalTimeoutError`, `ScreenMismatchError`, etc.
- **Wait States**: Intelligent polling of the "Input Inhibited" flag to prevent dropped keystrokes.
