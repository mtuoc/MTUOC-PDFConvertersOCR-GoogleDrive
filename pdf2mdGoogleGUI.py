import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Authorization scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service(log_callback):
    """Authenticates the user and returns the Drive service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log_callback("[*] Refreshing Google Drive credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("'credentials.json' not found in the current directory.")
            
            log_callback("[*] Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def run_ocr(input_pdf, output_md, log_callback, finish_callback):
    """Handles the heavy lifting of the OCR process in a separate thread."""
    try:
        log_callback("[*] Initializing Google Drive connection...")
        service = get_drive_service(log_callback)
        
        # If output file is not specified, generate it automatically
        if not output_md:
            output_md = os.path.splitext(input_pdf)[0] + ".md"
            
        log_callback(f"\n[>] Processing: {os.path.basename(input_pdf)} -> {os.path.basename(output_md)}")
        
        file_metadata = {
            'name': 'Temp_OCR_Document',
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(input_pdf, mimetype='application/pdf')
        
        log_callback("[*] Uploading PDF to Google Drive (converting to Google Doc)...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        log_callback("[*] Waiting for Google OCR to finish...")
        time.sleep(3)

        log_callback(f"[*] Exporting to Markdown format...")
        request = service.files().export_media(fileId=file_id, mimeType='text/markdown')
        content = request.execute()
        
        with open(output_md, 'wb') as f:
            f.write(content)

        log_callback("[*] Cleaning up Google Drive temporary files...")
        service.files().delete(fileId=file_id).execute()
        
        log_callback(f"[OK] Successfully saved: {output_md}")
        finish_callback(True, "Process completed successfully!")

    except FileNotFoundError as fnf:
        log_callback(f"[!] Error: {str(fnf)}")
        finish_callback(False, str(fnf))
    except Exception as e:
        log_callback(f"[!] Error processing file: {e}")
        finish_callback(False, f"An error occurred:\n{e}")


class PDF2MDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pdf2mdGoogle")
        self.root.geometry("1500x750")
        self.root.resizable(True, True)
        
        # Grid Configuration
        self.root.columnconfigure(1, weight=1)
        
        # --- Input File Section ---
        self.lbl_input = tk.Label(root, text="Input:")
        self.lbl_input.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 2))
        
        self.ent_input = tk.Entry(root, width=50)
        self.ent_input.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        self.btn_browse_in = tk.Button(root, text="Browse...", command=self.browse_input)
        self.btn_browse_in.grid(row=0, column=2, padx=(5, 10), pady=5)
        
        # --- Output File Section ---
        self.lbl_output = tk.Label(root, text="Output:")
        self.lbl_output.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 2))
        
        self.ent_output = tk.Entry(root, width=50)
        self.ent_output.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        self.btn_browse_out = tk.Button(root, text="Browse...", command=self.browse_output)
        self.btn_browse_out.grid(row=1, column=2, padx=(5, 10), pady=5)
        
        # --- Convert Button ---
        self.btn_convert = tk.Button(root, text="Convert", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", height=2, command=self.start_conversion)
        self.btn_convert.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=15)
        
        # --- Log / Console Output ---
        self.lbl_log = tk.Label(root, text="Process Log:")
        self.lbl_log.grid(row=5, column=0, sticky="w", padx=10, pady=(5, 2))
        
        self.txt_log = scrolledtext.ScrolledText(root, height=10, state='disabled', bg="#f4f4f4")
        self.txt_log.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 15))
        self.root.rowconfigure(6, weight=1)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Input PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if filename:
            self.ent_input.delete(0, tk.END)
            self.ent_input.insert(0, filename)
            
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Select Output Markdown File",
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if filename:
            self.ent_output.delete(0, tk.END)
            self.ent_output.insert(0, filename)

    def log(self, message):
        """Thread-safe logging mechanism to show info in the GUI text area."""
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def start_conversion(self):
        input_file = self.ent_input.get().strip()
        output_file = self.ent_output.get().strip()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input PDF file.")
            return
            
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "The specified input file does not exist.")
            return

        # Disable UI during execution to prevent multi-clicking
        self.btn_convert.config(state='disabled', text="Processing...", bg="#cccccc")
        self.txt_log.config(state='normal')
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.config(state='disabled')
        
        # Run the OCR task in a background thread so the GUI doesn't freeze/crash
        threading.Thread(
            target=run_ocr, 
            args=(input_file, output_file, self.log, self.on_conversion_finished),
            daemon=True
        ).start()

    def on_conversion_finished(self, success, message):
        """Brings back the UI functionality and displays a final message box."""
        self.btn_convert.config(state='normal', text="Convert", bg="#4CAF50")
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDF2MDApp(root)
    root.mainloop()
