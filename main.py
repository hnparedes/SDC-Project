import hashlib
import json
import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# For 7zip support
import py7zr

# PyCryptodome for hashing
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


# Common backend class for ACM
class AccessControlMatrix:
    # Setup user, file, and access lists
    def __init__(self):
        self.users = {}
        self.files = {}
        self.access_levels = []

    # Simple hashing function (SHA256)
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Function to add user with unique user ID, and their password and access levels. (TODO: Move to archiver class?)
    def add_user(self, uid, password, access_level):
        self.users[uid] = {
            "password_hash": self.hash_password(password),
            "access_level": access_level,
        }

    # Function to add access level to a file
    def add_file_permission(self, file_id, access_levels):
        self.files[file_id] = access_levels

    # JSON formatting helper
    def to_json(self):
        return {
            "users": self.users,
            "files": self.files,
            "access_levels": self.access_levels,
        }

    # JSON loader
    def load_json(self, data):
        self.users = data.get("users", {})
        self.files = data.get("files", {})
        self.access_levels = data.get("access_levels", [])


# Archiver backend class (TODO: Missing unfinalized SDC saving)
class SDCArchiver:
    # Setup ACM, document list, and key library for the archiver's later usage.
    def __init__(self):
        self.acm = AccessControlMatrix()
        self.documents = {}
        self.key_library = {}

    # Exports completed SDC
    def export_archive(self, archive_name, archive_password):
        temp_dir = tempfile.mkdtemp(prefix=".tempdir_sdc_")
        try:
            for fid, fpath in self.documents.items():
                # 32 bytes -> 256 bits
                key = get_random_bytes(32)
                self.key_library[fid] = key.hex()

                # Setup AES-256
                cipher = AES.new(key, AES.MODE_CBC)
                with open(fpath, "rb") as f:
                    data = f.read()

                encrypted_data = cipher.iv + cipher.encrypt(pad(data, AES.block_size))
                with open(os.path.join(temp_dir, fid), "wb") as f:
                    f.write(encrypted_data)

            with open(os.path.join(temp_dir, "acm.json"), "w") as f:
                json.dump(self.acm.to_json(), f)

            with open(os.path.join(temp_dir, "key_lib.json"), "w") as f:
                json.dump(self.key_library, f)

            with py7zr.SevenZipFile(
                archive_name, "w", password=archive_password
            ) as archive:
                archive.writeall(temp_dir, "sdc_contents")
            return True
        # Cover exception cases
        except Exception as e:
            raise e
        # Delete temp directory upon completion
        finally:
            shutil.rmtree(temp_dir)


# Viewer backend class
class SDCViewer:
    def __init__(self):
        # Setup variables for the viewer's later usage.
        self.temp_dir = None
        self.acm = AccessControlMatrix()
        self.key_library = {}
        self.current_user_level = None
        self.contents_dir = None

    # Function to open and attempt to access the SDC at the 7zip level
    def open_archive(self, archive_name, archive_password):
        self.temp_dir = tempfile.mkdtemp(prefix=".tempdir_viewer_")
        try:
            with py7zr.SevenZipFile(
                archive_name, "r", password=archive_password
            ) as archive:
                archive.extractall(path=self.temp_dir)
            self.contents_dir = os.path.join(self.temp_dir, "sdc_contents")

            with open(os.path.join(self.contents_dir, "acm.json"), "r") as f:
                self.acm.load_json(json.load(f))
            with open(os.path.join(self.contents_dir, "key_lib.json"), "r") as f:
                self.key_library = json.load(f)
            return True
        except py7zr.exceptions.BadPassword:
            self.close()
            return False
        except Exception as e:
            self.close()
            raise e

    # Function to authenicate with SDC
    def login(self, uid, password):
        user = self.acm.users.get(uid)
        if user and user["password_hash"] == self.acm.hash_password(password):
            self.current_user_level = user["access_level"]
            return True
        return False

    # Function to only access files (their titles specifically) permitted from the user's access levels
    def get_accessible_files(self):
        return [
            fid
            for fid, levels in self.acm.files.items()
            if self.current_user_level in levels
        ]

    # Function to extract a select file
    def extract_document(self, file_id, dest_path):
        key = bytes.fromhex(self.key_library[file_id])
        enc_filepath = os.path.join(self.contents_dir, file_id)

        # Read encrpyped file in binary mode
        with open(enc_filepath, "rb") as f:
            # IV -> Initialization Vector
            iv = f.read(16)
            ciphertext = f.read()

        # Decrypt the file
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

        # Write decrypted file in byte mode
        with open(dest_path, "wb") as f:
            f.write(decrypted_data)

    # Helper function to clear temp directory after closing viewer
    def close(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None


# GUI classes (TODO: Windows are rescaleable, leading to buttons being hidden. Set bounds to prevent this.)
# Author's notes: Some functions present here might be worth moving back to the backend classes?
# In addition, the archiver might be better with the documents on the right side and
# moving the ACM and users to the left. To be discussed and implemented later as needed.


# SDC Archiver GUI class
class ArchiverGUI(tk.Toplevel):
    # Setup window parameters
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SDC Archiver (Main Window)")
        self.geometry("800x550")
        self.backend = SDCArchiver()

        self.create_menu()
        self.create_widgets()

    # Create menu items
    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Draft Archive")
        file_menu.add_command(label="Save Draft")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Edit Details")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Tutorial")
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    # Create widgets to go within the menu
    def create_widgets(self):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Document list
        doc_frame = tk.LabelFrame(main_frame, text="Documents")
        doc_frame.place(relx=0, rely=0, relwidth=0.48, relheight=0.85)

        doc_btn_frame = tk.Frame(doc_frame)
        doc_btn_frame.pack(side=tk.BOTTOM, pady=5)
        # Button to add document
        tk.Button(doc_btn_frame, text="Add", width=8, command=self.add_document).pack(
            side=tk.LEFT, padx=2
        )
        # Button to edit document
        tk.Button(doc_btn_frame, text="Edit", width=8, command=self.edit_document).pack(
            side=tk.LEFT, padx=2
        )
        # Button to delete document
        tk.Button(
            doc_btn_frame,
            text="Delete",
            width=8,
            command=lambda: self.delete_tree_item(
                self.doc_tree, self.backend.documents
            ),
        ).pack(side=tk.LEFT, padx=2)

        # List out files along their access level
        self.doc_tree = ttk.Treeview(
            doc_frame, columns=("File", "Access Level"), show="headings"
        )
        self.doc_tree.heading("File", text="File")
        self.doc_tree.heading("Access Level", text="Access Level")
        self.doc_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top right: Access control levels
        al_frame = tk.LabelFrame(main_frame, text="Access Levels")
        al_frame.place(relx=0.52, rely=0, relwidth=0.48, relheight=0.4)

        al_btn_frame = tk.Frame(al_frame)
        al_btn_frame.pack(side=tk.BOTTOM, pady=5)
        # Add access level
        tk.Button(
            al_btn_frame, text="Add", width=8, command=self.add_access_level
        ).pack(side=tk.LEFT, padx=2)
        # Edit access levels
        tk.Button(
            al_btn_frame, text="Edit", width=8, command=self.edit_access_level
        ).pack(side=tk.LEFT, padx=2)
        # Delete access levels
        tk.Button(
            al_btn_frame,
            text="Delete",
            width=8,
            command=lambda: self.delete_tree_item(
                self.al_tree, self.backend.acm.access_levels, is_list=True
            ),
        ).pack(side=tk.LEFT, padx=2)

        self.al_tree = ttk.Treeview(al_frame, columns=("Name",), show="headings")
        self.al_tree.heading("Name", text="Name")
        self.al_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom right: User list
        user_frame = tk.LabelFrame(main_frame, text="Users")
        user_frame.place(relx=0.52, rely=0.45, relwidth=0.48, relheight=0.4)

        user_btn_frame = tk.Frame(user_frame)
        user_btn_frame.pack(side=tk.BOTTOM, pady=5)
        # Button to add user
        tk.Button(user_btn_frame, text="Add", width=8, command=self.add_user).pack(
            side=tk.LEFT, padx=2
        )
        # Button to edit user
        tk.Button(user_btn_frame, text="Edit", width=8, command=self.edit_user).pack(
            side=tk.LEFT, padx=2
        )
        # Button to delete user
        tk.Button(
            user_btn_frame,
            text="Delete",
            width=8,
            command=lambda: self.delete_tree_item(
                self.user_tree, self.backend.acm.users
            ),
        ).pack(side=tk.LEFT, padx=2)

        # Setup listing of user, access levels
        self.user_tree = ttk.Treeview(
            user_frame,
            columns=("Username", "Access Level"),
            show="headings",
        )
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Access Level", text="Access Level")
        self.user_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom left status bar.
        bottom_frame = tk.Frame(self, padx=10, pady=5)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_lbl = tk.Label(
            bottom_frame, text="Status: Waiting for input...", fg="gray"
        )
        self.status_lbl.pack(side=tk.LEFT)

        # Bottom right general buttons
        tk.Button(
            bottom_frame, text="Export SDC", width=12, command=self.export_sdc
        ).pack(side=tk.RIGHT, padx=5)
        # TODO: As mentioned before, this button does nothing.
        tk.Button(bottom_frame, text="Save", width=8).pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom_frame, text="Close", width=8, command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def refresh_sub_trees(self):
        """Helper to redraw users and documents if an Access Level is renamed."""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        for uid, udata in self.backend.acm.users.items():
            self.user_tree.insert("", "end", values=(uid, udata["access_level"], "***"))

        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)
        for fid in self.backend.documents.keys():
            levels = self.backend.acm.files.get(fid, [])
            self.doc_tree.insert("", "end", values=(fid, ", ".join(levels)))

    def delete_tree_item(self, tree, data_struct, is_list=False):
        selected = tree.selection()
        if not selected:
            return
        item_text = tree.item(selected[0])["values"][0]
        tree.delete(selected[0])
        if is_list:
            if item_text in data_struct:
                data_struct.remove(item_text)
        else:
            if item_text in data_struct:
                del data_struct[item_text]

    # Methods for adding
    def add_access_level(self):
        pop = tk.Toplevel(self)
        pop.title("Edit/Add Access Level")
        pop.geometry("250x100")
        tk.Label(pop, text="Name:").pack(pady=5)
        entry = tk.Entry(pop)
        entry.pack()

        def apply():
            lvl = entry.get().strip()
            if lvl and lvl not in self.backend.acm.access_levels:
                self.backend.acm.access_levels.append(lvl)
                self.al_tree.insert("", "end", values=(lvl,))
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

    def add_user(self):
        if not self.backend.acm.access_levels:
            messagebox.showerror("Error", "Create an Access Level first!")
            return
        pop = tk.Toplevel(self)
        pop.title("Edit/Add User")
        pop.geometry("250x200")

        tk.Label(pop, text="Username:").pack()
        u_entry = tk.Entry(pop)
        u_entry.pack()

        # TODO: Fails to deal with empty password entry, oops. It'll just not stop it from happening but also won't allow it?
        tk.Label(pop, text="Password:").pack()
        p_entry = tk.Entry(pop, show="*")
        p_entry.pack()

        tk.Label(pop, text="Access Level:").pack()
        cb = ttk.Combobox(pop, values=self.backend.acm.access_levels, state="readonly")
        cb.pack()

        def apply():
            usr = u_entry.get().strip()
            pwd = p_entry.get()
            lvl = cb.get()
            if usr and pwd and lvl:
                self.backend.acm.add_user(usr, pwd, lvl)
                self.user_tree.insert("", "end", values=(usr, lvl, "***"))
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

    # Editing occurs here. Welp.
    def add_document(self):
        if not self.backend.acm.access_levels:
            messagebox.showerror("Error", "Create an Access Level first!")
            return

        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        filename = os.path.basename(filepath)

        pop = tk.Toplevel(self)
        pop.title("Edit/Add Document")
        pop.geometry("300x250")

        tk.Label(pop, text=f"Path: {filepath}", wraplength=280).pack(pady=5)
        tk.Label(pop, text="Access Levels (Select multiple):").pack()

        lb = tk.Listbox(pop, selectmode=tk.MULTIPLE, height=5)
        for al in self.backend.acm.access_levels:
            lb.insert(tk.END, al)
        lb.pack(pady=5)

        def apply():
            selected_levels = [lb.get(i) for i in lb.curselection()]
            if selected_levels:
                self.backend.documents[filename] = filepath
                self.backend.acm.add_file_permission(filename, selected_levels)
                self.doc_tree.insert(
                    "", "end", values=(filename, ", ".join(selected_levels))
                )
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=5)

    # Editing methods
    def edit_access_level(self):
        selected = self.al_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an Access Level to edit.")
            return

        old_lvl = self.al_tree.item(selected[0])["values"][0]

        pop = tk.Toplevel(self)
        pop.title("Edit Access Level")
        pop.geometry("250x100")
        tk.Label(pop, text="Name:").pack(pady=5)

        entry = tk.Entry(pop)
        entry.insert(0, old_lvl)
        entry.pack()

        def apply():
            new_lvl = entry.get().strip()
            if (
                new_lvl
                and new_lvl != old_lvl
                and new_lvl not in self.backend.acm.access_levels
            ):
                # Update backend
                idx = self.backend.acm.access_levels.index(old_lvl)
                self.backend.acm.access_levels[idx] = new_lvl

                # Cascade change to users
                for uid, udata in self.backend.acm.users.items():
                    if udata["access_level"] == old_lvl:
                        udata["access_level"] = new_lvl

                # Cascade change to files
                for fid, levels in self.backend.acm.files.items():
                    if old_lvl in levels:
                        levels[levels.index(old_lvl)] = new_lvl

                # Update UI
                self.al_tree.item(selected[0], values=(new_lvl,))
                self.refresh_sub_trees()
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

    def edit_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a User to edit.")
            return

        old_uid = self.user_tree.item(selected[0])["values"][0]
        old_lvl = self.user_tree.item(selected[0])["values"][1]

        pop = tk.Toplevel(self)
        pop.title("Edit User")
        pop.geometry("250x200")

        tk.Label(pop, text="Username:").pack()
        u_entry = tk.Entry(pop)
        u_entry.insert(0, old_uid)
        u_entry.pack()

        tk.Label(pop, text="New Password (leave blank to keep):").pack()
        p_entry = tk.Entry(pop, show="*")
        p_entry.pack()

        tk.Label(pop, text="Access Level:").pack()
        cb = ttk.Combobox(pop, values=self.backend.acm.access_levels, state="readonly")
        cb.set(old_lvl)
        cb.pack()

        def apply():
            new_uid = u_entry.get().strip()
            new_pwd = p_entry.get()
            new_lvl = cb.get()

            if new_uid and new_lvl:
                old_hash = self.backend.acm.users[old_uid]["password_hash"]
                if new_uid != old_uid:
                    del self.backend.acm.users[old_uid]

                self.backend.acm.users[new_uid] = {
                    "password_hash": self.backend.acm.hash_password(new_pwd)
                    if new_pwd
                    else old_hash,
                    "access_level": new_lvl,
                }

                self.user_tree.item(selected[0], values=(new_uid, new_lvl, "***"))
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

    def edit_document(self):
        selected = self.doc_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a Document to edit.")
            return

        fid = self.doc_tree.item(selected[0])["values"][0]
        current_levels = self.backend.acm.files.get(fid, [])

        pop = tk.Toplevel(self)
        pop.title("Edit Document")
        pop.geometry("300x250")

        tk.Label(pop, text=f"File: {fid}", wraplength=280).pack(pady=5)
        tk.Label(pop, text="Access Levels (Select multiple):").pack()

        lb = tk.Listbox(pop, selectmode=tk.MULTIPLE, height=5)
        for i, al in enumerate(self.backend.acm.access_levels):
            lb.insert(tk.END, al)
            # Pre-highlight the currently assigned access levels
            if al in current_levels:
                lb.selection_set(i)
        lb.pack(pady=5)

        def apply():
            selected_levels = [lb.get(i) for i in lb.curselection()]
            if selected_levels:
                self.backend.acm.files[fid] = selected_levels
                self.doc_tree.item(
                    selected[0], values=(fid, ", ".join(selected_levels))
                )
            pop.destroy()

        tk.Button(pop, text="Apply", command=apply).pack(pady=5)

    # If you're looking for deletion methods, they were passed as lambda functions in the
    # GUI functions for deletion.
    # TODO: Check and see if that was a good idea. Probably wasn't.

    # SDC export GUI function
    def export_sdc(self):
        if not self.backend.documents:
            messagebox.showerror("Error", "Add at least one document.")
            return

        pop = tk.Toplevel(self)
        pop.title("Export SDC")
        pop.geometry("350x150")

        tk.Label(pop, text="Archive Key (Password):").pack(pady=5)
        pw_entry = tk.Entry(pop, show="*")
        pw_entry.pack(fill=tk.X, padx=20)

        def apply():
            pwd = pw_entry.get()
            if not pwd:
                messagebox.showerror("Error", "Archive Key is required.")
                return
            dest = filedialog.asksaveasfilename(
                defaultextension=".7z", filetypes=[("7z Archive", "*.7z")]
            )
            if dest:
                self.status_lbl.config(text="Exporting archive... Please wait.")
                self.update()
                try:
                    self.backend.export_archive(dest, pwd)
                    messagebox.showinfo("Success", "SDC Archive Exported Successfully!")
                    self.status_lbl.config(text="Export Complete.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export: {e}")
            pop.destroy()

        tk.Button(pop, text="Export", command=apply).pack(pady=15)


# SDC Viewer GUI class
class ViewerGUI(tk.Toplevel):
    def __init__(self, parent):
        # Set up SDC viewer window parameters
        super().__init__(parent)
        self.title("SDC Viewer")
        self.geometry("410x150")
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

        if self.backend.open_archive(path, pwd):
            self.title(f"SDC Viewer - {os.path.basename(path)}")
            self.create_auth_widgets()
        else:
            messagebox.showerror("Error", "Invalid Archive Key or corrupt SDC.")

    # Window for ACM authenciation
    def create_auth_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.geometry("300x150")

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
            if self.backend.login(u_entry.get(), p_entry.get()):
                # Create extraction window upon success
                self.create_extraction_widgets()
            else:
                messagebox.showerror("Error", "Login Failed. Invalid credentials.")

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


# Launcher class since I did all of this in one big file and I'm now paying the price.
# And I don't feel like commenting on all this since it's self explanatory really.
class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        # I just made this title up on the spot. ¯\_(ツ)_/¯
        self.title("SDC Suite")
        self.geometry("300x150")

        tk.Label(
            self, text="Secure Data Container (SDC)", font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="Launch SDC Archiver",
            width=20,
            pady=5,
            command=self.launch_archiver,
        ).pack(pady=5)
        tk.Button(
            btn_frame,
            text="Launch SDC Viewer",
            width=20,
            pady=5,
            command=self.launch_viewer,
        ).pack(pady=5)

    # Run archiver
    def launch_archiver(self):
        ArchiverGUI(self)

    # Run viewer
    def launch_viewer(self):
        ViewerGUI(self)


if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
