import tkinter as tk
from tkinter import messagebox
import hashlib
import random
import datetime

# Sample SIM database (IMSI: Ki)
sim_database = {
    '123456789012345': 'secretkey1',
    '987654321098765': 'secretkey2',
    '111122223333444': 'secretkey3'
}

# Registered SIMs: IMSI -> TMSI
registered_sims = {}

# --- Utility functions ---

def generate_rand():
    return str(random.randint(100000, 999999))

def generate_sres(rand, ki):
    combined = rand + ki
    return hashlib.sha256(combined.encode()).hexdigest()

def generate_tmsi():
    return str(random.randint(10000, 99999))

def log_to_file(filename, content):
    try:
        with open(filename, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            f.write(f"{timestamp} {content}\n")
    except Exception as e:
        messagebox.showerror("File Error", f"Error writing to log: {str(e)}")

# --- GUI App ---

class SIMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIM Card Communication Emulator")
        self.root.geometry("550x500")

        self.current_imsi = None

        self.build_gui()

    def build_gui(self):
        # Registration frame
        frame = tk.LabelFrame(self.root, text="SIM Registration", padx=10, pady=10)
        frame.pack(padx=10, pady=10, fill="both")

        tk.Label(frame, text="Enter IMSI:").grid(row=0, column=0)
        self.imsi_entry = tk.Entry(frame, width=25)
        self.imsi_entry.grid(row=0, column=1)

        tk.Button(frame, text="Register SIM", command=self.register_sim).grid(row=0, column=2, padx=5)

        self.status_label = tk.Label(frame, text="Status: Not Registered", fg="red")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Call simulation
        call_frame = tk.LabelFrame(self.root, text="Call Simulation", padx=10, pady=10)
        call_frame.pack(padx=10, pady=10, fill="both")

        tk.Label(call_frame, text="Call To IMSI:").grid(row=0, column=0)
        self.call_entry = tk.Entry(call_frame, width=25)
        self.call_entry.grid(row=0, column=1)

        tk.Button(call_frame, text="Call", command=self.simulate_call).grid(row=0, column=2, padx=5)

        # SMS simulation
        sms_frame = tk.LabelFrame(self.root, text="SMS Simulation", padx=10, pady=10)
        sms_frame.pack(padx=10, pady=10, fill="both")

        tk.Label(sms_frame, text="To IMSI:").grid(row=0, column=0)
        self.sms_to_entry = tk.Entry(sms_frame, width=25)
        self.sms_to_entry.grid(row=0, column=1)

        tk.Label(sms_frame, text="Message:").grid(row=1, column=0)
        self.sms_msg_entry = tk.Entry(sms_frame, width=35)
        self.sms_msg_entry.grid(row=1, column=1, columnspan=2)

        tk.Button(sms_frame, text="Send SMS", command=self.send_sms).grid(row=2, column=1, pady=5)

        # Log viewing
        log_btn = tk.Button(self.root, text="View Communication Log", command=self.view_log)
        log_btn.pack(pady=10)

    def register_sim(self):
        imsi = self.imsi_entry.get().strip()
        if imsi not in sim_database:
            messagebox.showerror("Error", "IMSI not found in database.")
            return

        rand = generate_rand()
        ki = sim_database[imsi]
        sres = generate_sres(rand, ki)

        expected_sres = generate_sres(rand, sim_database[imsi])
        if sres == expected_sres:
            tmsi = generate_tmsi()
            registered_sims[imsi] = tmsi
            self.current_imsi = imsi
            self.status_label.config(text=f"Registered: TMSI = {tmsi}", fg="green")
            log_to_file("communication_log.txt", f"SIM {imsi} authenticated successfully. Assigned TMSI {tmsi}")
        else:
            self.status_label.config(text="Authentication Failed", fg="red")
            messagebox.showerror("Auth Error", "Authentication failed")

    def simulate_call(self):
        if not self.current_imsi:
            messagebox.showerror("Error", "Register a SIM first.")
            return
        target_imsi = self.call_entry.get().strip()
        if target_imsi in registered_sims:
            log_to_file("communication_log.txt", f"Call: {self.current_imsi} ➝ {target_imsi} (Connected)")
            messagebox.showinfo("Call", f"Call to {target_imsi} connected!")
        else:
            log_to_file("communication_log.txt", f"Call: {self.current_imsi} ➝ {target_imsi} (Failed - Not Registered)")
            messagebox.showwarning("Call", f"Call failed. {target_imsi} is not registered.")

    def send_sms(self):
        if not self.current_imsi:
            messagebox.showerror("Error", "Register a SIM first.")
            return
        to_imsi = self.sms_to_entry.get().strip()
        message = self.sms_msg_entry.get().strip()
        if to_imsi in registered_sims:
            log_to_file("communication_log.txt", f"SMS: {self.current_imsi} ➝ {to_imsi}: {message}")
            log_to_file("sms_log.txt", f"From {self.current_imsi} ➝ {to_imsi}: {message}")
            messagebox.showinfo("SMS", f"Message sent to {to_imsi}")
        else:
            messagebox.showwarning("SMS", f"SMS failed. {to_imsi} not registered.")

    def view_log(self):
        try:
            with open("communication_log.txt", "r", encoding="utf-8") as f:
                logs = f.read()
            log_win = tk.Toplevel(self.root)
            log_win.title("Communication Log")
            text = tk.Text(log_win, wrap="word")
            text.insert("1.0", logs)
            text.pack(expand=True, fill="both")
        except Exception as e:
            messagebox.showerror("Log Error", f"Error reading log: {str(e)}")

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SIMApp(root)
    root.mainloop()
