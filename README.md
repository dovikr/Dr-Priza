# DR-Priza Automation Script

This repository contains a Python script that automates logging into the Priza website and fetching OTP codes from Gmail.

## Setup Instructions

Follow these steps to set up and run the script on your local machine.

### Prerequisites

- Python 3.x: [Download and install Python](https://www.python.org/). Ensure to check the option to add Python to the PATH during installation.

### Installation

1. **Clone the Repository**

    ```sh
    git clone https://github.com/yourusername/DR-Priza.git
    cd DR-Priza
    ```

2. **Install Required Libraries**

    Open a command prompt in the cloned repository directory and run:

    ```sh
    pip install -r requirements.txt
    ```

### Google API Setup

1. **Create Google API Keys**

    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project (or select an existing one).
    - Enable the Gmail API for your project.
    - Go to the "Credentials" section in the API & Services dashboard.
    - Click on "Create Credentials" and select "OAuth 2.0 Client IDs".
    - Set the application type to "Desktop app".
    - Download the JSON file and save it as `client_secret_oauth.json` in the same directory as this repository.

### Running the Script

1. **Prepare the Files**

    Ensure you have the following files in the same directory:
    - `DR-Priza.py`
    - `run_DR-Priza.bat`
    - `requirements.txt`
    - `client_secret_oauth.json` (created from the above steps)

    The `credentials.json` file will be created after the first run to store the username and password locally.

2. **Create and Configure `run_DR-Priza.bat`**

    Create a batch file named `run_DR-Priza.bat` with the following content:

    ```bat
    @echo off
    "C:\path\to\python.exe" "C:\path\to\DR-Priza.py"
    pause
    ```

    - Replace `"C:\path\to\python.exe"` with the path to your Python executable.
    - Replace `"C:\path\to\DR-Priza.py"` with the path to your Python script.

3. **Run the Script**

    - Double-click `run_DR-Priza.bat` to run the script.
    - The script will prompt you to authenticate with Google if it's the first time running it.
    - Follow the prompts to log in with your username and password.
    - The script will automatically navigate to the specified website and handle the OTP.

## Files Included

- `DR-Priza.py`: The main Python script.
- `requirements.txt`: List of Python dependencies.
- `run_DR-Priza.bat`: Batch file to run the script.
- `client_secret_oauth.json`: Google API credentials file (to be created by the user).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
