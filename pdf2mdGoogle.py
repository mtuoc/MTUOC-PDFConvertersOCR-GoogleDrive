import os
import argparse
import time
import glob
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Authorization scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Authenticates the user and returns the Drive service object."""
    creds = None
    # The token.json file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("[!] Error: 'credentials.json' not found in the current directory.")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def process_file(service, input_pdf, output_md=None):
    """Uploads a PDF, performs OCR, and saves the output as Markdown."""
    # Fixed syntax error here: added the colon (:)
    if output_md is None:
        output_md = os.path.splitext(input_pdf)[0] + ".md"
    
    print(f"\n[>] Processing: {input_pdf} -> {output_md}")
    
    try:
        file_metadata = {
            'name': 'Temp_OCR_Document',
            'mimeType': 'application/vnd.google-apps.document'  # Triggers Google Docs OCR
        }
        media = MediaFileUpload(input_pdf, mimetype='application/pdf')
        
        # 1. Upload and convert
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        # Short pause to allow Google's servers to finalize the OCR process
        time.sleep(3)

        # 2. Export directly to Markdown
        print(f"[*] Exporting '{input_pdf}' to Markdown format to '{output_md}'")
        request = service.files().export_media(fileId=file_id, mimeType='text/markdown')
        content = request.execute()
        
        with open(output_md, 'wb') as f:
            f.write(content)

        # 3. Clean up Google Drive
        service.files().delete(fileId=file_id).execute()
        print(f"[OK] Successfully saved: {output_md}")

    except Exception as e:
        print(f"[!] Error processing {input_pdf}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Batch OCR: PDF to Markdown via Google Drive API")
    parser.add_argument("pattern", help="File pattern or wildcard (e.g., '*.pdf' or 'letter_a_*.pdf')")
    
    # Added optional output argument. 'nargs="?"' makes it optional.
    parser.add_argument("output", nargs="?", help="Optional explicit output file name (works best for single files)", default=None)
    
    args = parser.parse_args()

    # Find all files matching the pattern
    files = glob.glob(args.pattern)
    
    # Filter to keep only PDF files (case insensitive)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"[!] No PDF files found matching the pattern: {args.pattern}")
        return

    print(f"[*] Found {len(pdf_files)} file(s) to process.")
    service = get_drive_service()

    # Sort files alphabetically to maintain dictionary order (e.g., chunk_01, chunk_02)
    sorted_files = sorted(pdf_files)
    
    for f in sorted_files:
        # If multiple files match a wildcard (e.g. *.pdf), providing a single output name 
        # would overwrite itself. We only use the explicit output argument if exactly one file matches.
        current_output = args.output if len(sorted_files) == 1 else None
        
        process_file(service, f, current_output)
        # Prevent hitting API rate limits
        time.sleep(2)

    print("\n[FINISH] All files have been processed successfully.")

if __name__ == "__main__":
    main()
