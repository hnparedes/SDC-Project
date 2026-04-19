import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sdc_archiver.archiver_backend import SDCArchiver

# GUI classes (TODO: Windows are rescaleable, leading to buttons being hidden. Set bounds to prevent this.)
# Author's notes: Some functions present here might be worth moving back to the backend classes?
# In addition, the archiver might be better with the documents on the right side and
# moving the ACM and users to the left. To be discussed and implemented later as needed.


# SDC Archiver GUI class
class ArchiverGUI(tk.Tk):
    # Setup window parameters
    def __init__(self):
        super().__init__()
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

        # Right side: Document list
        doc_frame = tk.LabelFrame(main_frame, text="Documents")
        doc_frame.place(relx=0.52, rely=0, relwidth=0.48, relheight=0.85)

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
            doc_btn_frame, text="Delete", width=8, command=self.delete_document
        ).pack(side=tk.LEFT, padx=2)

        # List out files along their access level
        self.doc_tree = ttk.Treeview(
            doc_frame, columns=("File", "Access Level"), show="headings"
        )
        self.doc_tree.heading("File", text="File")
        self.doc_tree.heading("Access Level", text="Access Level")
        self.doc_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top left: Access control levels
        al_frame = tk.LabelFrame(main_frame, text="Access Levels (Start Here)")
        al_frame.place(relx=0, rely=0, relwidth=0.48, relheight=0.4)

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
            al_btn_frame, text="Delete", width=8, command=self.delete_access_level
        ).pack(side=tk.LEFT, padx=2)

        self.al_tree = ttk.Treeview(al_frame, columns=("Name",), show="headings")
        self.al_tree.heading("Name", text="Name")
        self.al_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom left: User list
        user_frame = tk.LabelFrame(main_frame, text="Users")
        user_frame.place(relx=0, rely=0.45, relwidth=0.48, relheight=0.4)

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
            user_btn_frame, text="Delete", width=8, command=self.delete_user
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
        tk.Button(bottom_frame, text="Save", width=8, command=self.save_draft).pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom_frame, text="Close", width=8, command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def refresh_sub_trees(self):
        # Helper to redraw users and documents if an Access Level is renamed.
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        for uid, udata in self.backend.acm.users.items():
            self.user_tree.insert("", "end", values=(uid, udata["access_level"], "***"))

        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)
        for fid in self.backend.acm.documents.keys():
            levels = self.backend.acm.documents[fid].get("access_levels", [])
            self.doc_tree.insert("", "end", values=(fid, ", ".join(levels)))

    # Addition methods
    def add_access_level(self):
        pop = tk.Toplevel(self)
        pop.title("Edit/Add Access Level")
        pop.geometry("250x100")
        tk.Label(pop, text="Name:").pack(pady=5)
        entry = tk.Entry(pop)
        entry.pack()

        def apply():
            lvl = entry.get().strip()

            # Prevent creation of 'Unassigned'

            # Try adding the access level to the ACM
            try:
                self.backend.acm.add_access_level(lvl)
                # If it succeeds, update the access level treeview
                self.al_tree.insert("", "end", values=(lvl,))
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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
            # Try adding the user to the ACM
            try:
                self.backend.acm.add_user(usr, pwd, lvl)
                # If successful, update the user treeview
                self.user_tree.insert("", "end", values=(usr, lvl, "***"))
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

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
            # Try adding the document to the ACM
            try:
                self.backend.acm.add_document(filename, selected_levels, filepath)
                self.doc_tree.insert(
                    "", "end", values=(filename, ", ".join(selected_levels))
                )
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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

            # Try renaming the access level
            try:
                self.backend.acm.rename_access_level(old_lvl, new_lvl)
                # If successful, update all treeviews that are affected by the change
                self.al_tree.item(selected[0], values=(new_lvl,))
                self.refresh_sub_trees()
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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

            # Try updating the user information
            try:
                self.backend.acm.update_user(old_uid, new_uid, new_pwd, new_lvl)
                # If successful, update the user treeview
                self.user_tree.item(selected[0], values=(new_uid, new_lvl, "***"))
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(pop, text="Apply", command=apply).pack(pady=10)

    def edit_document(self):
        selected = self.doc_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a Document to edit.")
            return

        fid = self.doc_tree.item(selected[0])["values"][0]
        current_levels = self.backend.acm.documents[fid].get("access_levels", [])

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
            # Try updating the document permissions in the ACM
            try:
                self.backend.acm.set_document_perms(fid, selected_levels)
                # If successful, update the document treeview and record the file location
                self.doc_tree.item(
                    selected[0], values=(fid, ", ".join(selected_levels))
                )
                pop.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(pop, text="Apply", command=apply).pack(pady=5)

    # Deletion methods
    def delete_access_level(self):
        selected = self.al_tree.selection()
        if not selected:
            return

        lvl_to_delete = self.al_tree.item(selected[0])["values"][0]

        # Identify any users that are currently using this access level
        affected_users = self.backend.acm.get_users_with_access_level(lvl_to_delete)

        # Warn the user before proceeding with the deletion
        if affected_users:
            msg = (
                f"The following users are currently assigned to '{lvl_to_delete}':\n"
                f"{', '.join(affected_users)}\n\n"
                f"Their access level will be changed to 'Unassigned'. Do you wish to proceed?"
            )
            if not messagebox.askyesno("Confirm Deletion", msg):
                return
            else:
                if not messagebox.askyesno(
                    "Confirm Deletion",
                    f"Are you sure you want to delete the access level '{lvl_to_delete}'?",
                ):
                    return

        # Attempt to delete the access level
        try:
            self.backend.acm.delete_access_level(lvl_to_delete)
            # If successful, update the relevant treeviews
            self.al_tree.delete(selected[0])
            self.refresh_sub_trees()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            return

        uid = self.user_tree.item(selected[0])["values"][0]

        # Remove from user list and access control
        try:
            self.backend.acm.delete_user(uid)
            # Remove from UI tree
            self.user_tree.delete(selected[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_document(self):
        selected = self.doc_tree.selection()
        if not selected:
            return

        fid = self.doc_tree.item(selected[0])["values"][0]

        # Remove from file list and access control
        try:
            self.backend.acm.delete_document(fid)
            # Remove from UI tree
            self.doc_tree.delete(selected[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_draft(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON file", "*.json")]
        )
        if not filepath:
            return

        try:
            self.status_lbl.config(text="Saving...")
            self.backend.save_draft(filepath)
            messagebox.showinfo("Success", f"Successfully saved ACM to {str(filepath)}")
            self.status_lbl.config(text="Saving Complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_lbl.config(text="Saving Failed.")


    # SDC export GUI function
    def export_sdc(self):
        if not self.backend.acm.documents:
            messagebox.showerror("Error", "Add at least one document.")
            return

        # Check for unassigned users before continuing
        unassigned_users = [
            uid
            for uid, udata in self.backend.acm.users.items()
            if udata["access_level"] == "Unassigned"
        ]
        if unassigned_users:
            msg = (
                f"Warning: There are {len(unassigned_users)} user(s) with an 'Unassigned' access level.\n\n"
                f"These users will NOT be able to view any documents. Do you want to continue exporting?"
            )
            if not messagebox.askyesno("Unassigned Users Detected", msg):
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


if __name__ == "__main__":
    app = ArchiverGUI()
    app.mainloop()
