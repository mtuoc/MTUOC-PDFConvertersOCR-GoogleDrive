import os
import argparse
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Permissions
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def main():
    parser = argparse.ArgumentParser(description="Direct PDF to DOCX OCR via Google Drive")
    parser.add_argument("input", help="Input PDF file")
    # Made 'output' optional using nargs='?' and default=None
    parser.add_argument("output", nargs="?", help="Optional output DOCX file", default=None)
    args = parser.parse_args()

    # If output file is not specified, generate it using the input filename
    output_docx = args.output
    if output_docx is None:
        output_docx = os.path.splitext(args.input)[0] + ".docx"

    service = get_drive_service()

    print(f"[*] Uploading {args.input} to Google Drive for OCR processing...")
    
    file_metadata = {
        'name': 'Temp_OCR_Document',
        'mimeType': 'application/vnd.google-apps.document' # Converts to Google Doc
    }
    media = MediaFileUpload(args.input, mimetype='application/pdf')
    
    # 1. Upload and convert
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print(f"[*] Document converted. ID: {file_id}")

    # Give it a couple of seconds for Google to finish the internal OCR processing
    time.sleep(2)

    print(f"[*] Downloading file as {output_docx}...")
    
    # 2. Export directly to DOCX
    request = service.files().export_media(
        fileId=file_id, 
        mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    
    with open(output_docx, 'wb') as f:
        f.write(request.execute())

    # 3. Clean up Drive
    print("[*] Deleting temporary file from Drive...")
    service.files().delete(fileId=file_id).execute()
    
    print(f"\n[DONE] Your dictionary is located at: {output_docx}")

if __name__ == "__main__":
    main()
