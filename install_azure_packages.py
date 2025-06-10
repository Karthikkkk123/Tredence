import os
import subprocess
import sys
from typing import Dict, List, Optional

# Define Azure package groups
AZURE_PACKAGES = {
    "ai": [
        "azure-ai-textanalytics",
        "azure-cognitiveservices-vision-face",
        "azure-cognitiveservices-speech",
        "azure-cognitiveservices-personalizer",
    ],
    "communication": ["azure-communication-chat"],
    "data": ["azure-cosmos", "azure-synapse"],  # Fixed package name
    "common": ["streamlit", "python-dotenv", "pandas", "matplotlib", "networkx"],
    "llm": ["google-generativeai"],  # Added Google Generative AI package
}


def check_installation(package: str) -> bool:
    """Check if a package is already installed."""
    try:
        subprocess.run(
            [sys.executable, "-c", f"import {package.replace('-', '_')}"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_packages(
    packages: List[str], use_uv: bool = False, system: bool = False, user: bool = False
) -> Dict[str, bool]:
    """Install specified packages using pip or uv."""
    results = {}

    for package in packages:
        print(f"Installing {package}...")

        try:
            if use_uv:
                # UV requires --system flag if not in a virtual environment
                cmd = ["uv", "pip", "install", package]
                if system:
                    cmd.append("--system")
                elif not user:
                    # UV expects --system if not using a virtual environment
                    cmd.append("--system")
            else:
                cmd = [sys.executable, "-m", "pip", "install", package]
                if user:
                    cmd.append("--user")

            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            results[package] = True
            print(f"Successfully installed {package}")

        except subprocess.CalledProcessError as e:
            results[package] = False
            print(f"Failed to install {package}: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")

    return results


def main():
    """Main function to run the installer."""
    print("Azure Package Installer")
    print("======================")

    # Determine if uv is available
    use_uv = False
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        use_uv = True
        print("Using UV package manager")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Using standard pip")

    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if use_uv and not in_venv:
        print("Note: Not running in a virtual environment.")
        print("UV requires either --system flag or a virtual environment.")

    # Ask for installation mode
    print("\nSelect installation mode:")
    print("1. System-wide (requires admin privileges)")
    print("2. User-only (recommended for pip, not supported by uv)")
    print("3. Default (--system for uv, no flags for pip)")

    install_mode = input("Enter selection (1-3) [3]: ").strip() or "3"

    system_install = install_mode == "1" or (use_uv and install_mode != "2")
    user_install = install_mode == "2" and not use_uv

    if use_uv and install_mode == "2":
        print("\nWARNING: UV does not support user-only installation.")
        print("Falling back to system installation with --system flag.")
        system_install = True
        user_install = False

    # Select package groups to install
    print("\nAvailable package groups:")
    for group, packages in AZURE_PACKAGES.items():
        print(f"- {group}: {', '.join(packages)}")

    selected_groups = input(
        "\nEnter groups to install (comma-separated, or 'all'): "
    ).lower()

    # Collect packages to install
    to_install = []
    if selected_groups == "all":
        for packages in AZURE_PACKAGES.values():
            to_install.extend(packages)
    else:
        for group in selected_groups.split(","):
            group = group.strip()
            if group in AZURE_PACKAGES:
                to_install.extend(AZURE_PACKAGES[group])

    # Warn about system installation without admin privileges
    if system_install and not use_uv:
        print("\nWARNING: System-wide installation requires admin privileges.")
        print("If you're not running as administrator, installation will likely fail.")
        proceed = input("Continue with system installation? (y/N): ").lower() == "y"
        if not proceed:
            return

    # Install packages
    if to_install:
        print(f"\nInstalling {len(to_install)} packages...")
        results = install_packages(to_install, use_uv, system_install, user_install)

        # Show summary
        print("\nInstallation Summary:")
        succeeded = [pkg for pkg, success in results.items() if success]
        failed = [pkg for pkg, success in results.items() if not success]

        if succeeded:
            print(
                f"Successfully installed {len(succeeded)} packages: {', '.join(succeeded)}"
            )
        if failed:
            print(f"Failed to install {len(failed)} packages: {', '.join(failed)}")
            print(
                "\nNote: Some packages might not be available for your Python version or platform."
            )

            if "azure-synapse-analytics" in failed:
                print(
                    "Note: 'azure-synapse-analytics' was renamed to 'azure-synapse' in the latest versions."
                )

            if system_install and len(failed) > 0 and not use_uv:
                print("\nTIP: The failures might be due to permission issues.")
                print(
                    "Try running the script again with the user-only installation option,"
                )
                print("or run your terminal/command prompt as administrator.")

            if use_uv and len(failed) > 0:
                print("\nTIP for UV users:")
                print("To create and use a virtual environment with UV:")
                print("1. Run: uv venv")
                print("2. Activate the environment:")
                print("   - Windows: .venv\\Scripts\\activate")
                print("   - Unix/MacOS: source .venv/bin/activate")
                print("3. Run this script again")
    else:
        print("No packages selected for installation.")

    print("\nDone!")


if __name__ == "__main__":
    main()
