"""
This file contains code that interacts with the Google Drive API. 
"""

# =====
# SETUP
# =====
# The code below will help to set up the rest of the file.

# General import statements
from pathlib import Path
import io

# Importing different modules to help access Google Drive
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# =======
# METHODS
# =======
# Below, I'm going to define a number of methods that interact with the Google Drive API.


def generate_credentials(scopes):
    """
    This method will help with authentication by generating a `google_drive_auth_token.json` file,
    or by reading in the file if it already exists & is valid.
    """

    # Before we do anything, we'll set creds to None
    creds = None

    # First, check if the google_drive_auth_token.json file exists
    if Path("google_drive_auth_token.json").exists():
        creds = Credentials.from_authorized_user_file(
            "google_drive_auth_token.json", scopes
        )

    # If there are no valid credentials, let's generate some
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("google_drive_auth_token.json", "w") as token:
            token.write(creds.to_json())

    # Now that we have valid credentials, we can return them
    return creds


def download_google_sheet_as_excel(file_id, save_path):
    """
    This method will download a Google Sheet as an Excel file.
    """

    # First, we'll generate the credentials
    creds = generate_credentials(
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    # Next, we'll set up the Drive API client
    service = build("drive", "v3", credentials=creds)

    request = service.files().export_media(
        fileId=file_id,
        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    # Finally, we'll write the file to disk
    with open(save_path, "wb") as f:
        f.write(file.getvalue())
