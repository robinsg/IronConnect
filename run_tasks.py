import os
import sys
import subprocess
from datetime import datetime
from framework.core.config import IBMiConfig

def run_multi_system_tests(robot_file: str):
    """
    Orchestrates Robot Framework execution across different LPARs.
    Saves outputs into system-specific folders with timestamps.
    """
    # 1. Load config to get the host for folder naming
    config = IBMiConfig.load()
    
    # 2. Extract and sanitize system name
    # e.g., pub400.com -> pub400_com
    system_host = config.host or "localhost"
    system_folder = system_host.replace('.', '_').replace(':', '_')
    
    # 3. Create the results directory structure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = os.path.join("results", system_folder, timestamp)
    
    if not os.path.exists(output_base):
        os.makedirs(output_base)
        
    print(f"\n[IronConnect Orchestrator]")
    print(f"Target System    : {system_host}")
    print(f"Output Directory : {output_base}")
    print(f"Robot Suite      : {robot_file}")
    print("-" * 40)

    # 4. Prepare the Robot command
    # -d sets the directory for reports/logs/output
    # --variable sets metadata for the test suite
    cmd = [
        "robot",
        "-d", output_base,
        "--variable", f"SYSTEM_NAME:{system_host}",
        "--metadata", f"System:{system_host}",
        "--metadata", f"Environment:{config.device_type}",
        robot_file
    ]

    # 5. Execute with PYTHONPATH so Robot finds the 'framework' library
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    try:
        process = subprocess.run(cmd, env=env)
        print("-" * 40)
        if process.returncode == 0:
            print(f"SUCCESS: Result stored in {output_base}")
        else:
            print(f"FAILURE: Exit code {process.returncode}. Check logs in {output_base}")
    except FileNotFoundError:
        print("ERROR: 'robot' command not found. Please install via 'pip install robotframework'.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "tasks/login_tests.robot"
    run_multi_system_tests(target)
