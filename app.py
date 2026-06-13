import tkinter as tk
from tkinter import messagebox, ttk
import db

class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System - Desktop Admin")
        self.root.geometry("950x650")
        self.root.minsize(900, 600)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure theme colors
        self.primary_color = "#0f172a"  # Slate dark
        self.accent_color = "#3b82f6"   # Indigo
        self.bg_color = "#f8fafc"       # Slate light background
        
        self.root.configure(bg=self.bg_color)
        
        self.style.configure("TLabel", background=self.bg_color, font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), foreground=self.primary_color, background="white")
        self.style.configure("Tab.TFrame", background=self.bg_color)
        
        self.style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6)
        self.style.configure("Primary.TButton", background=self.accent_color, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#2563eb")])
        
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=26)
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e2e8f0", foreground="#1e293b")
        
        self.show_login()

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        login_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid", padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title_label = ttk.Label(login_frame, text="🏥 Hospital Admin Login", style="Header.TLabel", background="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(login_frame, text="Username", background="white").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(login_frame, width=25, font=("Helvetica", 10))
        self.username_entry.grid(row=1, column=1, pady=5)
        self.username_entry.focus()
        
        ttk.Label(login_frame, text="Password", background="white").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*", width=25, font=("Helvetica", 10))
        self.password_entry.grid(row=2, column=1, pady=5)
        
        self.password_entry.bind("<Return>", lambda event: self.handle_login())
        
        login_btn = ttk.Button(login_frame, text="Login", command=self.handle_login, style="Primary.TButton")
        login_btn.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky="ew")

    def handle_login(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get()
        
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        if db.authenticate_user(user, pwd):
            messagebox.showinfo("Success", "Login Successful")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🏥 Hospital Management Portal", fg="white", bg=self.primary_color, font=("Helvetica", 14, "bold"))
        title_label.pack(side="left", padx=20)
        
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.show_login)
        logout_btn.pack(side="right", padx=20)
        
        # Notebook container for Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Patients
        self.patients_tab = ttk.Frame(self.notebook, style="Tab.TFrame")
        self.notebook.add(self.patients_tab, text=" Patients Database ")
        self.setup_patients_tab()
        
        # Tab 2: Billing
        self.billing_tab = ttk.Frame(self.notebook, style="Tab.TFrame")
        self.notebook.add(self.billing_tab, text=" Invoices & Billing ")
        self.setup_billing_tab()

    # --- PATIENTS TAB CONFIG ---

    def setup_patients_tab(self):
        # Controls (Search & Add)
        ctrl_frame = tk.Frame(self.patients_tab, bg=self.bg_color)
        ctrl_frame.pack(fill="x", side="top", padx=10, pady=10)
        
        ttk.Label(ctrl_frame, text="Search Patients:").pack(side="left")
        self.p_search = ttk.Entry(ctrl_frame, width=25)
        self.p_search.pack(side="left", padx=5)
        self.p_search.bind("<KeyRelease>", lambda e: self.load_patients())
        
        ttk.Button(ctrl_frame, text="Filter", command=self.load_patients).pack(side="left", padx=2)
        ttk.Button(ctrl_frame, text="Clear", command=self.clear_p_search).pack(side="left", padx=2)
        ttk.Button(ctrl_frame, text="+ Register Patient", command=self.open_patient_dialog).pack(side="right", padx=5)
        
        # Patients Tree Table
        table_frame = tk.Frame(self.patients_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "name", "age", "gender", "blood", "city", "phone", "email")
        self.p_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        self.p_tree.heading("id", text="ID")
        self.p_tree.heading("name", text="Name")
        self.p_tree.heading("age", text="Age")
        self.p_tree.heading("gender", text="Gender")
        self.p_tree.heading("blood", text="Blood")
        self.p_tree.heading("city", text="City")
        self.p_tree.heading("phone", text="Phone")
        self.p_tree.heading("email", text="Email")
        
        self.p_tree.column("id", width=50, anchor="center")
        self.p_tree.column("name", width=150)
        self.p_tree.column("age", width=50, anchor="center")
        self.p_tree.column("gender", width=70, anchor="center")
        self.p_tree.column("blood", width=60, anchor="center")
        self.p_tree.column("city", width=100)
        self.p_tree.column("phone", width=110)
        self.p_tree.column("email", width=150)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.p_tree.yview)
        self.p_tree.configure(yscrollcommand=vsb.set)
        
        self.p_tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="right")
        
        # Actions Frame
        act_frame = tk.Frame(self.patients_tab, bg=self.bg_color)
        act_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        
        ttk.Button(act_frame, text="✏️ Edit Selected", command=self.edit_patient).pack(side="left", padx=5)
        ttk.Button(act_frame, text="🗑️ Delete Selected", command=self.delete_patient).pack(side="left", padx=5)
        
        self.p_tree.bind("<Double-1>", lambda e: self.edit_patient())
        self.load_patients()

    def load_patients(self):
        for item in self.p_tree.get_children():
            self.p_tree.delete(item)
        query = self.p_search.get().strip()
        records = db.get_patients(query if query else None)
        for r in records:
            self.p_tree.insert("", "end", values=(
                r["id"], r["name"], r["age"], r["gender"] or "-", r["blood_group"] or "-", r["city"], r["phone"] or "-", r["email"] or "-"
            ))

    def clear_p_search(self):
        self.p_search.delete(0, "end")
        self.load_patients()

    def open_patient_dialog(self, p_data=None):
        is_edit = p_data is not None
        title = "Edit Patient Info" if is_edit else "Register Patient"
        
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("460x420")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dlg_frame = tk.Frame(dialog, padx=20, pady=20)
        dlg_frame.pack(fill="both", expand=True)
        
        # Fields layout
        ttk.Label(dlg_frame, text="Name: *").grid(row=0, column=0, sticky="w", pady=4)
        name_ent = ttk.Entry(dlg_frame, width=28)
        name_ent.grid(row=0, column=1, pady=4)
        if is_edit: name_ent.insert(0, p_data["name"])
        
        ttk.Label(dlg_frame, text="Age: *").grid(row=1, column=0, sticky="w", pady=4)
        age_ent = ttk.Entry(dlg_frame, width=28)
        age_ent.grid(row=1, column=1, pady=4)
        if is_edit: age_ent.insert(0, p_data["age"])
        
        ttk.Label(dlg_frame, text="Gender:").grid(row=2, column=0, sticky="w", pady=4)
        gender_cb = ttk.Combobox(dlg_frame, values=["Male", "Female", "Other"], state="readonly", width=26)
        gender_cb.grid(row=2, column=1, pady=4)
        if is_edit and p_data["gender"] in ["Male", "Female", "Other"]: gender_cb.set(p_data["gender"])
        
        ttk.Label(dlg_frame, text="Blood Group:").grid(row=3, column=0, sticky="w", pady=4)
        blood_cb = ttk.Combobox(dlg_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly", width=26)
        blood_cb.grid(row=3, column=1, pady=4)
        if is_edit and p_data["blood"]: blood_cb.set(p_data["blood"])
        
        ttk.Label(dlg_frame, text="City: *").grid(row=4, column=0, sticky="w", pady=4)
        city_ent = ttk.Entry(dlg_frame, width=28)
        city_ent.grid(row=4, column=1, pady=4)
        if is_edit: city_ent.insert(0, p_data["city"])
        
        ttk.Label(dlg_frame, text="Phone:").grid(row=5, column=0, sticky="w", pady=4)
        phone_ent = ttk.Entry(dlg_frame, width=28)
        phone_ent.grid(row=5, column=1, pady=4)
        if is_edit and p_data["phone"] != "-": phone_ent.insert(0, p_data["phone"])
        
        ttk.Label(dlg_frame, text="Email:").grid(row=6, column=0, sticky="w", pady=4)
        email_ent = ttk.Entry(dlg_frame, width=28)
        email_ent.grid(row=6, column=1, pady=4)
        if is_edit and p_data["email"] != "-": email_ent.insert(0, p_data["email"])
        
        ttk.Label(dlg_frame, text="Emerg. Contact Name:").grid(row=7, column=0, sticky="w", pady=4)
        ec_name_ent = ttk.Entry(dlg_frame, width=28)
        ec_name_ent.grid(row=7, column=1, pady=4)
        if is_edit and p_data["ec_name"]: ec_name_ent.insert(0, p_data["ec_name"])
        
        ttk.Label(dlg_frame, text="Emerg. Contact Phone:").grid(row=8, column=0, sticky="w", pady=4)
        ec_phone_ent = ttk.Entry(dlg_frame, width=28)
        ec_phone_ent.grid(row=8, column=1, pady=4)
        if is_edit and p_data["ec_phone"]: ec_phone_ent.insert(0, p_data["ec_phone"])
        
        def save():
            name = name_ent.get().strip()
            age_s = age_ent.get().strip()
            city = city_ent.get().strip()
            gender = gender_cb.get() or None
            blood = blood_cb.get() or None
            phone = phone_ent.get().strip() or None
            email = email_ent.get().strip() or None
            ec_name = ec_name_ent.get().strip() or None
            ec_phone = ec_phone_ent.get().strip() or None
            
            if not name or not age_s or not city:
                messagebox.showerror("Error", "Name, Age, and City are required!", parent=dialog)
                return
            try:
                age = int(age_s)
                if age <= 0 or age > 150: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Age must be a positive integer between 1 and 150", parent=dialog)
                return
                
            try:
                if is_edit:
                    db.update_patient(p_data["id"], name, age, city, phone, email, gender, blood, ec_name, ec_phone)
                    messagebox.showinfo("Success", "Patient details updated", parent=dialog)
                else:
                    db.add_patient(name, age, city, phone, email, gender, blood, ec_name, ec_phone)
                    messagebox.showinfo("Success", "Patient registered successfully", parent=dialog)
                dialog.destroy()
                self.load_patients()
                self.load_billing() # Refresh billing tables in case names changed
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}", parent=dialog)
                
        btn_fr = tk.Frame(dlg_frame)
        btn_fr.grid(row=9, column=0, columnspan=2, pady=15, sticky="e")
        ttk.Button(btn_fr, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="Save", command=save, style="Primary.TButton").pack(side="left", padx=5)
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def edit_patient(self):
        sel = self.p_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a patient to edit")
            return
        vals = self.p_tree.item(sel)["values"]
        # Pull details
        p_data = {
            "id": vals[0], "name": vals[1], "age": vals[2], "gender": vals[3], "blood": vals[4], "city": vals[5], "phone": vals[6], "email": vals[7]
        }
        # Get full row from database to get emergency details too
        patients_list = db.get_patients()
        for p in patients_list:
            if p["id"] == p_data["id"]:
                p_data["ec_name"] = p["emergency_contact_name"]
                p_data["ec_phone"] = p["emergency_contact_phone"]
                break
                
        self.open_patient_dialog(p_data)

    def delete_patient(self):
        sel = self.p_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a patient to delete")
            return
        vals = self.p_tree.item(sel)["values"]
        pid, pname = vals[0], vals[1]
        if messagebox.askyesno("Confirm Delete", f"Delete patient '{pname}'? This deletes all associated billing/appointment records."):
            db.delete_patient(pid)
            messagebox.showinfo("Deleted", "Patient deleted successfully")
            self.load_patients()
            self.load_billing()

    # --- BILLING TAB CONFIG ---

    def setup_billing_tab(self):
        ctrl_frame = tk.Frame(self.billing_tab, bg=self.bg_color)
        ctrl_frame.pack(fill="x", side="top", padx=10, pady=10)
        
        ttk.Label(ctrl_frame, text="Search Invoices:").pack(side="left")
        self.b_search = ttk.Entry(ctrl_frame, width=25)
        self.b_search.pack(side="left", padx=5)
        self.b_search.bind("<KeyRelease>", lambda e: self.load_billing())
        
        ttk.Button(ctrl_frame, text="Filter", command=self.load_billing).pack(side="left", padx=2)
        ttk.Button(ctrl_frame, text="Clear", command=self.clear_b_search).pack(side="left", padx=2)
        ttk.Button(ctrl_frame, text="+ Issue Invoice", command=self.open_billing_dialog).pack(side="right", padx=5)
        
        table_frame = tk.Frame(self.billing_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = ("id", "patient_name", "total", "paid", "due", "method", "status")
        self.b_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        self.b_tree.heading("id", text="Invoice ID")
        self.b_tree.heading("patient_name", text="Patient Name")
        self.b_tree.heading("total", text="Total Amount")
        self.b_tree.heading("paid", text="Paid Amount")
        self.b_tree.heading("due", text="Due Amount")
        self.b_tree.heading("method", text="Payment Method")
        self.b_tree.heading("status", text="Payment Status")
        
        self.b_tree.column("id", width=80, anchor="center")
        self.b_tree.column("patient_name", width=200)
        self.b_tree.column("total", width=100, anchor="e")
        self.b_tree.column("paid", width=100, anchor="e")
        self.b_tree.column("due", width=100, anchor="e")
        self.b_tree.column("method", width=120, anchor="center")
        self.b_tree.column("status", width=120, anchor="center")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.b_tree.yview)
        self.b_tree.configure(yscrollcommand=vsb.set)
        
        self.b_tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="right")
        
        act_frame = tk.Frame(self.billing_tab, bg=self.bg_color)
        act_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        
        ttk.Button(act_frame, text="✏️ Edit Selected", command=self.edit_billing).pack(side="left", padx=5)
        ttk.Button(act_frame, text="🗑️ Delete Selected", command=self.delete_billing).pack(side="left", padx=5)
        
        self.b_tree.bind("<Double-1>", lambda e: self.edit_billing())
        self.load_billing()

    def load_billing(self):
        for item in self.b_tree.get_children():
            self.b_tree.delete(item)
        query = self.b_search.get().strip()
        records = db.get_billing_records(query if query else None)
        for r in records:
            due = float(r["total_amount"]) - float(r["paid_amount"])
            self.b_tree.insert("", "end", values=(
                f"#{r['id']}", r["patient_name"], f"${r['total_amount']}", f"${r['paid_amount']}", f"${due:.2f}", r["payment_method"] or "-", r["payment_status"]
            ))

    def clear_b_search(self):
        self.b_search.delete(0, "end")
        self.load_billing()

    def open_billing_dialog(self, b_data=None):
        is_edit = b_data is not None
        title = "Adjust Invoice Settings" if is_edit else "Create Invoice"
        
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dlg_frame = tk.Frame(dialog, padx=20, pady=20)
        dlg_frame.pack(fill="both", expand=True)
        
        # Load Patient selections
        patients = db.get_patients()
        if not patients:
            messagebox.showwarning("Warning", "Register at least one patient first!", parent=dialog)
            dialog.destroy()
            return
            
        patient_options = [f"{p['name']} (ID: {p['id']})" for p in patients]
        
        ttk.Label(dlg_frame, text="Select Patient: *").grid(row=0, column=0, sticky="w", pady=6)
        patient_cb = ttk.Combobox(dlg_frame, values=patient_options, state="readonly", width=26)
        patient_cb.grid(row=0, column=1, pady=6)
        
        if is_edit:
            # Match selection
            for item in patient_options:
                if f"ID: {b_data['patient_id']}" in item:
                    patient_cb.set(item)
                    break
            patient_cb.configure(state="disabled") # Disable changing patient during edit
        else:
            patient_cb.current(0)
            
        ttk.Label(dlg_frame, text="Total Amount ($): *").grid(row=1, column=0, sticky="w", pady=6)
        total_ent = ttk.Entry(dlg_frame, width=28)
        total_ent.grid(row=1, column=1, pady=6)
        if is_edit: total_ent.insert(0, str(b_data["total"]))
        
        ttk.Label(dlg_frame, text="Paid Amount ($):").grid(row=2, column=0, sticky="w", pady=6)
        paid_ent = ttk.Entry(dlg_frame, width=28)
        paid_ent.grid(row=2, column=1, pady=6)
        paid_ent.insert(0, str(b_data["paid"]) if is_edit else "0.00")
        
        ttk.Label(dlg_frame, text="Payment Status:").grid(row=3, column=0, sticky="w", pady=6)
        status_cb = ttk.Combobox(dlg_frame, values=["Unpaid", "Partially Paid", "Paid"], state="readonly", width=26)
        status_cb.grid(row=3, column=1, pady=6)
        status_cb.set(b_data["status"] if is_edit else "Unpaid")
        
        ttk.Label(dlg_frame, text="Payment Method:").grid(row=4, column=0, sticky="w", pady=6)
        method_cb = ttk.Combobox(dlg_frame, values=["Cash", "Card", "Insurance"], state="readonly", width=26)
        method_cb.grid(row=4, column=1, pady=6)
        if is_edit and b_data["method"] != "-": method_cb.set(b_data["method"])
        
        def save():
            selected_patient = patient_cb.get()
            total_s = total_ent.get().strip()
            paid_s = paid_ent.get().strip()
            status = status_cb.get()
            method = method_cb.get() or None
            
            if not selected_patient or not total_s:
                messagebox.showerror("Error", "Patient and Total Amount are required!", parent=dialog)
                return
                
            try:
                # Extract patient ID from string format: "Name (ID: 3)"
                patient_id = int(selected_patient.split("ID: ")[1].split(")")[0])
                total = float(total_s)
                paid = float(paid_s) if paid_s else 0.0
                if total < 0 or paid < 0: raise ValueError
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Amounts must be valid non-negative numbers", parent=dialog)
                return
                
            try:
                if is_edit:
                    db.update_billing(b_data["id"], patient_id, total, paid, status, method)
                    messagebox.showinfo("Success", "Invoice updated", parent=dialog)
                else:
                    db.add_billing(patient_id, total, paid, status, method)
                    messagebox.showinfo("Success", "Invoice created successfully", parent=dialog)
                dialog.destroy()
                self.load_billing()
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}", parent=dialog)
                
        btn_fr = tk.Frame(dlg_frame)
        btn_fr.grid(row=5, column=0, columnspan=2, pady=15, sticky="e")
        ttk.Button(btn_fr, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="Save", command=save, style="Primary.TButton").pack(side="left", padx=5)
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def edit_billing(self):
        sel = self.b_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an invoice to edit")
            return
        vals = self.b_tree.item(sel)["values"]
        # Clean ID (strip '#')
        bid = int(str(vals[0]).replace("#", ""))
        
        # Get billing record info
        records = db.get_billing_records()
        billing_record = None
        for r in records:
            if r["id"] == bid:
                billing_record = r
                break
                
        if billing_record:
            b_data = {
                "id": bid,
                "patient_id": billing_record["patient_id"],
                "total": billing_record["total_amount"],
                "paid": billing_record["paid_amount"],
                "status": billing_record["payment_status"],
                "method": billing_record["payment_method"] or "-"
            }
            self.open_billing_dialog(b_data)

    def delete_billing(self):
        sel = self.b_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an invoice to delete")
            return
        vals = self.b_tree.item(sel)["values"]
        bid = int(str(vals[0]).replace("#", ""))
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove invoice #{bid}?"):
            db.delete_billing(bid)
            messagebox.showinfo("Deleted", "Invoice deleted successfully")
            self.load_billing()

if __name__ == "__main__":
    try:
        db.initialize_db()
    except Exception as e:
        print(f"Warning: Database startup error: {e}")
        
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()