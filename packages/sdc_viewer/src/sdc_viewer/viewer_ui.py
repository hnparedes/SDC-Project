import os
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from sdc_viewer.viewer_backend import SDCViewer
except ModuleNotFoundError:
    messagebox.showerror("Error", "AC key not found! Exiting...")
    exit()

# SDC Viewer GUI class
class ViewerGUI(tk.Tk):
    def __init__(self):
        # Set up SDC viewer window parameters
        super().__init__()
        self.title("SDC Viewer")
        self.geometry("410x150")
        self.resizable(False, False)
        self.backend = SDCViewer()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_open_widgets()

    # Create window widgets
    def create_open_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Prompts for SDC location and archive key
        tk.Label(self, text="SDC Location:").grid(
            row=0, column=0, padx=10, pady=15, sticky="e"
        )
        self.loc_entry = tk.Entry(self, width=25)
        self.loc_entry.grid(row=0, column=1)
        tk.Button(self, text="...", command=self.browse_archive).grid(
            row=0, column=2, padx=5
        )

        tk.Label(self, text="Archive Key:").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.key_entry = tk.Entry(self, show="*", width=25)
        self.key_entry.grid(row=1, column=1)

        # Buttons to close the viewer and open an SDC
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=15)
        tk.Button(btn_frame, text="Close", width=8, command=self.on_close).pack(
            side=tk.LEFT, padx=10
        )
        tk.Button(btn_frame, text="Open", width=8, command=self.open_archive).pack(
            side=tk.LEFT, padx=10
        )

    # Function to select an SDC
    def browse_archive(self):
        # Call OS file browser
        path = filedialog.askopenfilename(filetypes=[("7z Archive", "*.7z")])
        if path:
            self.loc_entry.delete(0, tk.END)
            self.loc_entry.insert(0, path)

    # Function to attempt opening an SDC
    def open_archive(self):
        path = self.loc_entry.get()
        pwd = self.key_entry.get()
        if not path or not pwd:
            messagebox.showwarning("Warning", "Please provide location and key.")
            return
        try:
            if self.backend.open_archive(path, pwd):
                self.title(f"SDC Viewer - {os.path.basename(path)}")
                self.create_auth_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            return

    # Window for ACM authenciation
    def create_auth_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.geometry("300x150")
        self.resizable(False, False)

        tk.Label(self, text="Authenticate", font=("Helvetica", 12, "bold")).pack(pady=5)

        frame = tk.Frame(self)
        frame.pack()
        tk.Label(frame, text="Username:").grid(row=0, column=0, pady=5)
        u_entry = tk.Entry(frame)
        u_entry.grid(row=0, column=1)

        tk.Label(frame, text="Password:").grid(row=1, column=0, pady=5)
        p_entry = tk.Entry(frame, show="*")
        p_entry.grid(row=1, column=1)

        # Function to attempt ACM authenication
        def attempt_login():
            try:
                self.backend.login(u_entry.get(), p_entry.get())
                # Create extraction window upon success
                self.create_extraction_widgets()
            except Exception as e:
                messagebox.showerror("Error", "Login Failed. Invalid credentials.")
                return

        # Buttons to cancel authenication or to attempt login
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Cancel", width=8, command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Login", width=8, command=attempt_login).pack(
            side=tk.LEFT, padx=5
        )

    # Function to create window and extract documents from SDC
    def create_extraction_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.geometry("350x300")
        self.resizable(False, False)

        tk.Label(self, text="Select Documents / Files to Extract", anchor="w").pack(
            fill=tk.X, padx=10, pady=5
        )

        files = self.backend.get_accessible_files()
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        for f in files:
            self.listbox.insert(tk.END, f)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10)

        ext_frame = tk.Frame(self)
        ext_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(ext_frame, text="Extract to:").grid(row=0, column=0)
        self.dest_entry = tk.Entry(ext_frame, width=20)
        self.dest_entry.grid(row=0, column=1, padx=5)
        tk.Button(ext_frame, text="...", command=self.browse_dest).grid(row=0, column=2)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Cancel", width=8, command=self.on_close).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Extract", width=8, command=self.extract_files).pack(
            side=tk.LEFT, padx=5
        )

    def browse_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, path)

    def extract_files(self):
        selections = [self.listbox.get(i) for i in self.listbox.curselection()]
        dest = self.dest_entry.get()

        if not selections:
            messagebox.showwarning("Warning", "Select at least one file.")
            return
        if not dest or not os.path.exists(dest):
            messagebox.showwarning("Warning", "Select a valid destination directory.")
            return

        for fid in selections:
            try:
                self.backend.extract_document(fid, os.path.join(dest, fid))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decrypt {fid}:\n{e}")
                return

        messagebox.showinfo(
            "Success", f"Extracted {len(selections)} document(s) successfully."
        )
        self.on_close()

    def on_close(self):
        self.backend.close()
        self.destroy()


if __name__ == "__main__":
    app = ViewerGUI()
    app.mainloop()
