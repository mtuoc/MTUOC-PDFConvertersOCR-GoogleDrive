# MTUOC-PDFConvertersOCR-GoogleDrive
Scripts and programs to convert PDF to documents formats and perform OCR using GoogleDrive

A collection of lightweight Python utilities that leverage the Google Drive API to perform high-quality Optical Character Recognition (OCR) on PDF files, exporting them directly into editable Markdown (.md) or Microsoft Word (.docx) formats. This repository includes both a scriptable Command Line Interface (CLI) version and an intuitive Graphical User Interface (GUI).
Features

    High-Accuracy OCR: Utilizes Google Docs' native OCR engine to extract text from scanned PDFs.

    Dual Output Support: Convert PDFs to standard Markdown or fully formatted Word documents.

    Flexible Automation: Run batch tasks via the CLI or use the standalone desktop GUI application.

    Smart Fallbacks: Optional output paths; if omitted, the system automatically names the file after the source input.

    Asynchronous Execution: The GUI runs conversions on a background thread to prevent application freezing.

Prerequisites & Installation

Before running the applications, ensure you have Python 3.7+ installed.

    Clone the Repository:
    Bash

    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME

    Install Required Dependencies:
    Bash

    pip install google-auth google-auth-oauthlib google-auth-transport-requests google-api-python-client

    (Note: tkinter is required for the GUI version. It comes pre-installed with standard Python distributions on Windows and macOS. Linux users may need to install it via sudo apt-get install python3-tk).

Setting Up Google Drive API (credentials.json)

To interact with the Google Drive API, you must authenticate your application by obtaining a client secrets configuration file from the Google Cloud Console.
Step-by-Step Guide:

    Create a Google Cloud Project:

        Go to the Google Cloud Console.

        Click on the project dropdown in the top-left corner and select New Project.

        Name your project (e.g., PDF-OCR-Tool) and click Create.

    Enable the Google Drive API:

        In the sidebar, navigate to APIs & Services > Library.

        Search for Google Drive API.

        Click on it and select Enable.

    Configure the OAuth Consent Screen:

        Navigate to APIs & Services > OAuth consent screen.

        Select External and click Create.

        Fill in the required app information (App name, User support email, Developer contact information). You can leave optional fields blank.

        Click Save and Continue through the Scopes and Test users screens.

        Crucial: Go back to the OAuth consent screen dashboard and under Publishing status, ensure it is set to Testing. Under Test users, add the specific Google Account email address you intend to use for scanning documents.

    Generate Credentials:

        Navigate to APIs & Services > Credentials.

        Click + Create Credentials at the top and select OAuth client ID.

        Set the Application type to Desktop app.

        Name your client (e.g., OCR Desktop Client) and click Create.

    Download the JSON file:

        A dialog box will appear confirming the creation. Click Download JSON.

        Rename the downloaded file to exactly credentials.json.

        Place credentials.json directly into the root directory of this project.

    Note on token.json: The first time you execute any script, your default web browser will automatically open, prompting you to log in to your Google Account and grant permission. Once authorized, a file named token.json will be generated locally. This token caches your session so you will not need to authenticate via the browser on subsequent runs.

Usage
1. Graphical User Interface (GUI)

Perfect for interactive, single-file conversions.

    Launch the Application:
    Bash

    python gui_converter.py

    How to use:

        Click the first Browse... button to select your target PDF file.

        (Optional) Click the second Browse... button to specify a custom destination path and filename. If left blank, it will automatically output to the same directory with the correct extension (.docx or .md).

        Click Convert. The integrated log window will display real-time progress updates.

2. Command Line Interface (CLI)

Ideal for scripting, scheduling, or keyboard-driven workflows.

    Convert PDF to Markdown (.md):
    Bash

    python cli_to_md.py "path/to/document.pdf" ["optional/output/path.md"]

    (Supports wildcard patterns such as *.pdf for batch processing multiple documents).

    Convert PDF to Word (.docx):
    Bash

    python cli_to_docx.py "path/to/document.pdf" ["optional/output/path.docx"]
