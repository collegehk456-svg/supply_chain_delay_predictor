#!/usr/bin/env python
"""
Initialization script for SmartShip AI project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def create_directories():
    print_header("📁 Creating Project Directories")
    
    directories = [
        "data/raw", "data/processed", "data/features",
        "models/production", "models/staging", "models/archived",
        "logs", "notebooks"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        gitkeep.touch()
        print_success(f"Created {directory}/")

def check_python_version():
    print_header("🐍 Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print_info(f"Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version_str} is supported")
        return True
    else:
        print_error(f"Python 3.9+ required")
        return False

def setup_environment():
    print_header("⚙️  Setting Up Environment")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print_success(".env file created")
        print_warning("Update .env with your credentials")
    elif env_file.exists():
        print_info(".env already exists")

def install_dependencies():
    print_header("📦 Installing Dependencies")
    
    if not Path("requirements.txt").exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        print_info("Installing packages...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"]
        )
        print_success("Dependencies installed")
        
        print_info("Installing Generative AI support...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "google-generativeai"]
        )
        print_success("google-generativeai installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Installation failed: {e}")
        return False

def main():
    print(f"{Colors.BOLD}{Colors.GREEN}\n🚀 SmartShip AI - Project Initialization\n{Colors.RESET}")
    
    if not check_python_version():
        sys.exit(1)
    
    create_directories()
    setup_environment()
    
    if not install_dependencies():
        sys.exit(1)
    
    print_header("✨ Setup Complete!")
    print_success("Environment is ready!")
    print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
    print("1. Configure .env with your API keys")
    print("2. Run: python scripts/download_and_train.py --download")
    print("3. Start API: uvicorn backend.main:app --reload --port 8000")
    print("4. Start Dashboard: streamlit run frontend/main.py\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)
