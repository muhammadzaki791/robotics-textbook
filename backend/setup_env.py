import subprocess
import sys
import os

def create_virtual_environment():
    """Create a Python virtual environment for the backend."""
    print("Creating virtual environment...")

    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("Virtual environment created successfully.")

    # Determine the path to pip in the virtual environment
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        python_path = os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/MacOS
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

    # Install requirements
    print("Installing dependencies from requirements.txt...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

    print("\nVirtual environment setup complete!")
    print(f"Virtual environment created in: {os.path.abspath('venv')}")
    print(f"Dependencies installed from requirements.txt")
    print("\nTo activate the virtual environment:")
    if os.name == 'nt':
        print("  Windows: venv\\Scripts\\activate")
    else:
        print("  Unix/Linux/Mac: source venv/bin/activate")

if __name__ == "__main__":
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    create_virtual_environment()