#!/usr/bin/env python3
"""
Super-Resolution Microscopy Application Setup Script
Windows Development Environment Setup

This script sets up the development environment for Windows contributors.
It creates a virtual environment and installs all required dependencies.

Usage:
    python setup_environment.py
    OR
    Double-click setup_environment.bat

Requirements:
    - Python 3.10 (required for PySpin compatibility)
    - Windows 10/11
    - pip (usually comes with Python)
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output (Windows 10+ supports these)"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKBLUE):
    """Print colored message to terminal"""
    try:
        print(f"{color}{message}{Colors.ENDC}")
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(message.encode(encoding, errors="replace").decode(encoding))

def print_header(message):
    """Print a header message"""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f" {message}", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)

def print_success(message):
    """Print a success message"""
    print_colored(f"SUCCESS: {message}", Colors.OKGREEN)

def print_warning(message):
    """Print a warning message"""
    print_colored(f"WARNING: {message}", Colors.WARNING)

def print_error(message):
    """Print an error message"""
    print_colored(f"ERROR: {message}", Colors.FAIL)

def check_windows_version():
    """Check if running on Windows"""
    if os.name != 'nt':
        print_error("This setup script is designed for Windows only!")
        print_error("Please use the appropriate setup for your operating system.")
        return False
    
    print_success("Running on Windows")
    return True

def check_python_version():
    """Check if Python 3.10 is available"""
    print_header("Checking Python Version")
    
    # Check if Python 3.10 is available via py launcher
    try:
        result = subprocess.run(["py", "-3.10", "--version"], 
                              capture_output=True, text=True, check=True)
        version_str = result.stdout.strip()
        print_success(f"Python 3.10 found: {version_str}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Python 3.10 is required but not found!")
        print_error("Please install Python 3.10 from: https://www.python.org/downloads/")
        print_error("Make sure to check 'Add Python to PATH' during installation!")
        print_error("")
        print_error("Note: This application requires Python 3.10 for PySpin compatibility.")
        return False

def check_pip():
    """Check if pip is available"""
    print_header("Checking pip")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print_success(f"pip is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pip is not available!")
        print_error("Please reinstall Python with pip included.")
        return False

def create_virtual_environment(venv_path):
    """Create a virtual environment using Python 3.10"""
    print_header("Creating Virtual Environment")
    
    if venv_path.exists():
        print_warning(f"Virtual environment already exists at {venv_path}")
        response = input("Do you want to recreate it? (y/N): ").lower().strip()
        if response == 'y':
            print("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print_success("Using existing virtual environment")
            return True
    
    try:
        print(f"Creating virtual environment at {venv_path} with Python 3.10...")
        # Use py launcher to create venv with Python 3.10
        subprocess.run(["py", "-3.10", "-m", "venv", str(venv_path)], 
                      check=True, capture_output=True, text=True)
        print_success("Virtual environment created successfully with Python 3.10")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        print_error("Make sure Python 3.10 is installed and accessible via 'py -3.10'")
        return False
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def get_python_executable(venv_path):
    """Get the Python executable path in the virtual environment"""
    return str(venv_path / "Scripts" / "python.exe")

def install_dependencies(venv_path, requirements_file):
    """Install dependencies using pip"""
    print_header("Installing Dependencies")
    
    python_exe = get_python_executable(venv_path)
    
    if not Path(python_exe).exists():
        print_error(f"Python executable not found at {python_exe}")
        return False
    
    if not requirements_file.exists():
        print_error(f"Requirements file not found: {requirements_file}")
        return False
    
    try:
        print("Upgrading pip...")
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True, text=True)
        print_success("pip upgraded successfully")
        
        print("Installing build tools (setuptools, wheel)...")
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"], 
                      check=True, capture_output=True, text=True)
        print_success("Build tools installed successfully")
        
        print(f"Installing dependencies from {requirements_file}...")
        print("This may take a few minutes...")
        
        # First try: Install all dependencies at once
        try:
            result = subprocess.run([python_exe, "-m", "pip", "install", "-r", str(requirements_file), "--no-warn-script-location"], 
                                  check=True, capture_output=True, text=True, timeout=300)
            print_success("Dependencies installed successfully")
            
            # Install pycobolt from GitHub (not in requirements.txt)
            try:
                print("Installing pycobolt from GitHub...")
                subprocess.run([python_exe, "-m", "pip", "install", "git+https://github.com/cobolt-lasers/pycobolt.git", "--no-warn-script-location"], 
                              check=True, capture_output=True, text=True, timeout=120)
                print_success("pycobolt (Cobolt laser control)")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print_warning("Failed to install pycobolt from GitHub")
                print_warning("  pycobolt is required for the Acquire laser")
            
            # Try to install PySpin from local wheel file in Acquire/Req/
            pyspin_installed = False
            project_root = Path(__file__).parent.absolute()
            pyspin_wheel = project_root / "Acquire" / "Req" / "spinnaker_python-4.0.0.116-cp310-cp310-win_amd64.whl"
            
            if pyspin_wheel.exists():
                try:
                    print(f"Found PySpin wheel: {pyspin_wheel.name}")
                    print("Installing PySpin from local wheel...")
                    subprocess.run([python_exe, "-m", "pip", "install", str(pyspin_wheel), "--no-warn-script-location"], 
                                  check=True, capture_output=True, text=True, timeout=120)
                    print_success("PySpin (FLIR camera control)")
                    pyspin_installed = True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    print_warning("Failed to install PySpin from local wheel")
                    print_warning(f"  Error: {e}")
            else:
                # Fallback: try to find any spinnaker wheel in project root
                pyspin_wheels = list(project_root.glob('spinnaker_python-*.whl'))
                if pyspin_wheels:
                    try:
                        print(f"Found PySpin wheel: {pyspin_wheels[0].name}")
                        print("Installing PySpin from local wheel...")
                        subprocess.run([python_exe, "-m", "pip", "install", str(pyspin_wheels[0]), "--no-warn-script-location"], 
                                      check=True, capture_output=True, text=True, timeout=120)
                        print_success("PySpin (FLIR camera control)")
                        pyspin_installed = True
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                        print_warning("Failed to install PySpin from local wheel")
                        print_warning(f"  Error: {e}")
            
            if not pyspin_installed:
                print("")
                print_warning("PySpin (FLIR camera SDK) not found or failed to install:")
                print_warning(f"  Expected location: {pyspin_wheel}")
                print_warning("  Option 1: Place spinnaker_python-*.whl file in Acquire/Req/ folder")
                print_warning("  Option 2: Manual installation:")
                print_warning("    1. Visit: https://www.flir.com/products/spinnaker-sdk/")
                print_warning("    2. Download Spinnaker SDK + PySpin wheel for your Python version")
                print_warning("    3. Install SDK first, then: pip install spinnaker_python-*.whl")
                print_warning("  PySpin is required for the Acquire autofocus camera")
            
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print_warning("Bulk installation failed, trying individual package installation...")
            
            # Second try: Install packages one by one
            return install_packages_individually(python_exe, requirements_file)
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install build tools!")
        print_error("Error details:")
        print(e.stderr)
        return False

def install_packages_individually(python_exe, requirements_file):
    """Install packages one by one as a fallback method"""
    print("Installing packages individually...")
    
    # Read requirements file and extract package names
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    # Core packages that should be installed first
    core_packages = [
        "setuptools>=45.0.0",
        "wheel>=0.37.0",
        "numpy<2.0",  # PySpin requires NumPy 1.x, not 2.x
        "PyQt5>=5.15.0",
        "opencv-python>=4.5.0",
        "pyserial>=3.4",
        "pco>=0.1.0",
    ]
    
    failed_packages = []
    
    for package in core_packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([python_exe, "-m", "pip", "install", package, "--no-warn-script-location"], 
                          check=True, capture_output=True, text=True, timeout=120)
            print_success(f"{package.split('>=')[0]}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print_warning(f"Failed to install {package}")
            failed_packages.append(package)
    
    # Install pycobolt from GitHub
    try:
        print("Installing pycobolt from GitHub...")
        subprocess.run([python_exe, "-m", "pip", "install", "git+https://github.com/cobolt-lasers/pycobolt.git", "--no-warn-script-location"], 
                      check=True, capture_output=True, text=True, timeout=120)
        print_success("pycobolt (Cobolt laser control)")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print_warning("Failed to install pycobolt from GitHub")
        print_warning("  pycobolt is required for the Acquire laser")
        failed_packages.append("pycobolt")

    if failed_packages:
        print_warning(f"Some packages failed to install: {failed_packages}")
        print_warning("The Acquire application needs these packages to start.")
        return False
    else:
        print_success("All core packages installed successfully!")
        return True

def test_installation(venv_path):
    """Test if the installation was successful"""
    print_header("Testing Installation")
    
    python_exe = get_python_executable(venv_path)
    
    # Test core imports
    core_imports = [
        "PyQt5.QtWidgets",
        "numpy",
        "cv2",
        "serial",
        "pco",
        "pycobolt",
        "PySpin",
    ]
    
    failed_imports = []
    
    for module in core_imports:
        try:
            subprocess.run([python_exe, "-c", f"import {module}"], 
                          check=True, capture_output=True, text=True, timeout=30)
            print_success(f"{module}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print_error(f"{module}")
            failed_imports.append(module)
    
    if failed_imports:
        print_warning(f"\nSome modules failed to import: {', '.join(failed_imports)}")
        print_warning("The Acquire application cannot start until these imports work.")
        return False
    else:
        print_success("\nAll core modules imported successfully!")
        return True

def print_final_instructions(venv_path, project_root):
    """Print final setup instructions"""
    print_header("Setup Complete!")
    
    print_colored("Windows development environment setup completed!", Colors.OKGREEN)
    print()
    print_colored("Virtual environment created at:", Colors.OKBLUE)
    print_colored(f"  {venv_path}", Colors.OKCYAN)
    print()
    print_colored("To start the application:", Colors.OKBLUE)
    print()
    print_colored("   Double-click Launch_Application.bat", Colors.OKCYAN)
    print()
    print_colored("Tips:", Colors.OKCYAN)
    print_colored("  - The launcher uses the virtual environment automatically", Colors.OKBLUE)

def main():
    """Main setup function"""
    print_colored("Super-Resolution Microscopy Application Setup", Colors.HEADER)
    print_colored("Windows Development Environment Setup", Colors.OKBLUE)
    print()
    
    # Get project root directory
    project_root = Path(__file__).parent.absolute()
    venv_path = project_root / "venv"
    requirements_file = project_root / "requirements.txt"
    
    print(f"Project root: {project_root}")
    print(f"Virtual environment will be created at: {venv_path}")
    print()
    
    # Check prerequisites
    if not check_windows_version():
        return False
    
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Create virtual environment
    if not create_virtual_environment(venv_path):
        return False
    
    # Install dependencies
    if not install_dependencies(venv_path, requirements_file):
        print_warning("Some dependencies failed to install, but continuing...")
    
    # Test installation
    test_success = test_installation(venv_path)
    
    if test_success:
        print_final_instructions(venv_path, project_root)
    
    return test_success

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print_colored("\nSetup completed successfully!", Colors.OKGREEN)
            print_colored("You can now start developing!", Colors.OKGREEN)
            input("\nPress Enter to exit...")
            sys.exit(0)
        else:
            print_colored("\nSetup completed with warnings.", Colors.WARNING)
            print_colored("Check the output above for any issues.", Colors.WARNING)
            input("\nPress Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print_colored("\n\nSetup interrupted by user.", Colors.FAIL)
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\nSetup failed with error: {e}", Colors.FAIL)
        input("\nPress Enter to exit...")
        sys.exit(1)
