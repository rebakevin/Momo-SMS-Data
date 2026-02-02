#!/usr/bin/env python3
"""
Cross-platform launcher for Momo SMS Data API
Works on Windows, Linux, and macOS
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

if platform.system() == "Windows":
    # Enable ANSI colors on Windows 10+
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        RED = '\033[0;31m'
        NC = '\033[0m'
    except:
        GREEN = YELLOW = RED = NC = ''
else:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_colored(message, color):
    print(f"{color}{message}{NC}")

def run_command(command, shell=False, check=True):
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print_colored(f"Error running command: {e}", RED)
        return False

def main():
    """Main launcher function"""
    print_colored("Starting Momo SMS Data API...\n", GREEN)
    
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    if platform.system() == "Windows":
        venv_dir = project_root / "venv"
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        activate_script = venv_dir / "Scripts" / "activate.bat"
    else:
        venv_dir = project_root / "venv"
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
        activate_script = venv_dir / "bin" / "activate"
    
    # Check if venv exists
    if not venv_dir.exists():
        print_colored("Virtual environment not found. Creating...", YELLOW)
        if run_command([sys.executable, "-m", "venv", "venv"]):
            print_colored("✓ Virtual environment created\n", GREEN)
        else:
            print_colored("✗ Failed to create virtual environment", RED)
            sys.exit(1)
    
    # Check if dependencies are installed
    try:
        result = subprocess.run(
            [str(python_exe), "-c", "import apispec"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise ImportError
    except:
        print_colored("Installing dependencies...", YELLOW)
        
        # Upgrade pip
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "-q"],
            check=False
        )
        
        # Install requirements
        if (project_root / "requirements.txt").exists():
            result = subprocess.run(
                [str(pip_exe), "install", "-r", "requirements.txt", "-q"]
            )
            if result.returncode == 0:
                print_colored("✓ Dependencies installed\n", GREEN)
            else:
                print_colored("✗ Failed to install dependencies", RED)
                sys.exit(1)
        else:
            print_colored("✗ requirements.txt not found", RED)
            sys.exit(1)
    
            sys.exit(1)
    
    print_colored("Checking for existing server...", YELLOW)
    if platform.system() == "Windows":
        subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *main.py*"],
            capture_output=True,
            check=False
        )
    else:
        subprocess.run(
            ["pkill", "-f", "python.*main.py"],
            capture_output=True,
            check=False
        )
    
    # Start the server
    print_colored("Server starting...\n", GREEN)
    
    try:
        # Run the main application
        subprocess.run([str(python_exe), "main.py"])
    except KeyboardInterrupt:
        print_colored("\n\nServer stopped by user", YELLOW)
    except Exception as e:
        print_colored(f"\n✗ Server error: {e}", RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
