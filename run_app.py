import subprocess
import sys
from pathlib import Path


def main():
    """
    Helper script to properly start the Streamlit application
    """
    # Get the directory of this script
    script_dir = Path(__file__).parent

    # Define path to the app.py file
    app_path = script_dir / "streamlit-app" / "src" / "app.py"

    if not app_path.exists():
        print(f"Error: Could not find app at {app_path}")
        sys.exit(1)

    print(f"Starting Streamlit app at {app_path}")
    print("--------------------------------------")

    # Check if .env file exists in the streamlit-app directory
    env_path = script_dir / "streamlit-app" / ".env"
    if not env_path.exists():
        print("Warning: .env file not found at the expected location.")
        print(f"Expected location: {env_path}")
        print("The app may not work properly without environment variables.")

    # Build the command to run Streamlit
    cmd = ["streamlit", "run", str(app_path)]

    # Use subprocess to run the Streamlit command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to run Streamlit app.")
        print("Make sure Streamlit is installed by running: pip install streamlit")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit command not found.")
        print("Make sure Streamlit is installed by running: pip install streamlit")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
