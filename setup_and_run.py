import subprocess
import sys

def install_requirements():
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_script():
    print("Starting Reddit Terminal Reader...")
    subprocess.call([sys.executable, "main.py"])

if __name__ == "__main__":
    install_requirements()
    run_script()
