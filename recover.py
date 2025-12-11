import os
import sys
from cryptography.fernet import Fernet
from tkinter import *
from tkinter import messagebox
from threading import Thread

# =========================================================================
# CONFIGURATION
# =========================================================================
TARGET_DIR = os.path.dirname(os.path.abspath(__file__)) 
KEY_FILE = os.path.join(TARGET_DIR, "encryption_key.log")
PATH_LOG_FILE = os.path.join(TARGET_DIR, "lab_files_list.log")
EXTENSION = ".apollyon"

class DecrypterEngine:
    def __init__(self):
        self.key = None
        self.fernet = None
        self.paths = None
        
    def load_artifacts(self):
        try:
            # 1. Load the Key Artifact
            with open(KEY_FILE, 'rb') as k:
                self.key = k.read()
            self.fernet = Fernet(self.key)
            
            # 2. Load the Path Log Artifact
            with open(PATH_LOG_FILE, 'r') as p:
                self.paths = [line.strip() for line in p if line.strip()]
            
            messagebox.showinfo("Triage Complete", f"Key and Path Log loaded.\n{len(self.paths)} files ready for decryption.")
            return True
                
        except FileNotFoundError as e:
            messagebox.showerror("Error: Artifacts Missing", f"Could not find required files: {e.filename}. Artifact collection failed.")
            return False
        except Exception as e:
            messagebox.showerror("Error: Artifact Corrupted", f"Failed to load artifacts. They may be corrupted: {e}")
            return False

    def decrypt_file(self, file_path):
        if not file_path.endswith(EXTENSION):
            return True # Skip non-encrypted files
            
        try:
            # Read encrypted content
            with open(file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()

            # Decrypt
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Write decrypted data back and rename
            new_path = file_path.replace(EXTENSION, "")
            with open(new_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)
            
            # Remove the original encrypted file
            os.remove(file_path)
            return True
            
        except Exception:
            # File decrypt error (could be corrupted, or wrong key/engine)
            return False

    def run_recovery(self):
        if not self.paths:
            messagebox.showwarning("Warning", "No paths loaded. Run Triage first.")
            return
            
        success_count = 0
        total_count = len(self.paths)
        
        for path in self.paths:
            if self.decrypt_file(path):
                success_count += 1
                
        if success_count == total_count:
            messagebox.showinfo("Recovery Success", f"ALL {success_count} files successfully recovered.")
            # Final cleanup: Remove logs after successful decryption
            os.remove(KEY_FILE)
            os.remove(PATH_LOG_FILE)
        else:
            messagebox.showwarning("Recovery Incomplete", f"{success_count}/{total_count} files recovered. Check logs manually.")
# =========================================================================
# 3. GUI for Tool
# =========================================================================
        
def start_tool_gui():
    window = Tk()
    window.title("APOLLYON INCIDENT TRIAGE/RECOVERY TOOL")
    window.geometry("500x300")
    window.resizable(False, False)
    window.configure(bg="#1c2833")
    
    engine = DecrypterEngine()

    def handle_triage():
        Thread(target=engine.load_artifacts).start()

    def handle_recovery():
        # Requires successful triage first
        Thread(target=engine.run_recovery).start()

    title_label = Label(window, text="DEFENSIVE RECOVERY TOOL", bg="#1c2833", fg="#2ecc71", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    triage_button = Button(window, text="1. RUN ARTIFACT TRIAGE (LOAD KEY/PATH LOG)", command=handle_triage, bg="#2c3e50", fg="white", font=("Arial", 12))
    triage_button.pack(pady=10, padx=50, fill=X)
    
    decrypt_button = Button(window, text="2. START DECRYPTION/RECOVERY", command=handle_recovery, bg="#3498db", fg="white", font=("Arial", 12))
    decrypt_button.pack(pady=10, padx=50, fill=X)

    status_label = Label(window, text="Tool for authorized security simulation only.", bg="#1c2833", fg="#95a5a6", font=("Arial", 9))
    status_label.pack(pady=5)

    window.mainloop()

if __name__ == '__main__':
    start_tool_gui()
