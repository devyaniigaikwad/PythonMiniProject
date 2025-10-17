import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- 1. Database Setup ---
DATABASE_NAME = 'simple_vit_tracker.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY,
            name TEXT, email TEXT UNIQUE, branch TEXT, year INTEGER,
            cgpa REAL, dsa_solved INTEGER, major_projects INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# --- 2. Placement Criteria (Logic) ---
CRITERIA = {
    "CS": {"CGPA_MIN": 8.5, "DSA_MIN": 150, "JOB_FOCUS": "Software Dev, Cloud"},
    "IT": {"CGPA_MIN": 8.0, "DSA_MIN": 150, "JOB_FOCUS": "Full Stack Dev, Cybersecurity"},
    "ECS": {"CGPA_MIN": 7.5, "DSA_MIN": 150, "JOB_FOCUS": "Embedded Systems, IoT"},
    "EXTC": {"CGPA_MIN": 7.0, "DSA_MIN": 150, "JOB_FOCUS": "Telecom Engineer, VLSI"},
}
PROJECTS_MIN_GOAL = 2 

def get_guidance(profile):
    if not profile or profile.get('branch') is None: return "Please complete your profile.", []
    
    branch = profile['branch']
    criteria = CRITERIA.get(branch, CRITERIA['CS'])
    guidance = []
    is_ready = True
    
    # Check 1: CGPA
    if profile['cgpa'] < criteria['CGPA_MIN']:
        is_ready = False
        guidance.append(f"❌ CGPA ({profile['cgpa']:.1f}) is below {criteria['CGPA_MIN']:.1f}.")
    else: guidance.append("✅ CGPA is strong.")
        
    # Check 2: DSA (Minimum 150)
    if profile['dsa_solved'] < criteria['DSA_MIN']:
        is_ready = False
        guidance.append(f"❌ DSA ({profile['dsa_solved']}) is below the new goal of {criteria['DSA_MIN']}. Practice daily!")
    else: guidance.append("✅ DSA practice is good.")

    # Check 3: Projects (Minimum 2)
    if profile['major_projects'] < PROJECTS_MIN_GOAL:
        is_ready = False
        guidance.append(f"⚠️ Need at least {PROJECTS_MIN_GOAL} major projects. Build one now.")
    else: guidance.append("✅ Projects portfolio is solid.")
        
    guidance.append(f"💡 Suitable Roles: {criteria['JOB_FOCUS']}")

    summary = "🎉 READY! Start interviews." if is_ready else "🚨 NEEDS FOCUS! Check the ❌ areas."
    return summary, guidance

# --- 3. GUI Application ---
class SimpleVITTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple VIT Placement Tracker")
        self.geometry("700x550")
        self.configure(bg='#f5f9ff') # Main window background color
        init_db()
        self.current_email = None

        self._setup_styles()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.login_tab = ttk.Frame(self.notebook, style='TFrame'); self.notebook.add(self.login_tab, text=' Login ')
        self.dashboard_tab = ttk.Frame(self.notebook, style='TFrame'); self.notebook.add(self.dashboard_tab, text=' Dashboard ', state='disabled')

        self._setup_login_tab()
        self._setup_dashboard_tab()

    def _setup_styles(self):
        style = ttk.Style(self)
        
        # General Theming
        style.theme_use('clam') # Clam theme is often better for custom colors
        
        # Custom Frame and Tab Background
        style.configure('TFrame', background='#ffffff') # White background for the frames inside the notebook
        style.configure('TNotebook', background='#f5f9ff', borderwidth=0)
        style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), background='#e0e6f1', foreground='#333333')
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')], foreground=[('selected', '#004d99')])

        # Custom Labels (Header and Standard)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), foreground='#004d99', background='#ffffff')
        style.configure('TLabel', background='#ffffff')
        
        # Custom Buttons
        style.configure('TButton', font=('Helvetica', 10, 'bold'), background='#005a99', foreground='white', borderwidth=0)
        style.map('TButton', background=[('active', '#003366')])
        
        # Custom LabelFrames (Boxes)
        style.configure('TLabelframe', background='#ffffff', bordercolor='#dddddd')
        style.configure('TLabelframe.Label', background='#ffffff', foreground='#004d99')
        
        # Custom Listbox Styling
        self.option_add('*Listbox*Background', '#f9f9f9')
        self.option_add('*Listbox*Foreground', '#333333')
        self.option_add('*Listbox*Font', ('Helvetica', 10))

    def _setup_login_tab(self):
        frame = ttk.Frame(self.login_tab, padding="30"); frame.pack(expand=True)
        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.email_entry = ttk.Entry(frame, width=30); self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text="Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.name_entry = ttk.Entry(frame, width=30); self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Branch:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.branch_var = tk.StringVar(value='CS')
        ttk.Combobox(frame, textvariable=self.branch_var, values=list(CRITERIA.keys()), state='readonly', width=28).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Year:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.year_var = tk.IntVar(value=4)
        ttk.Combobox(frame, textvariable=self.year_var, values=[1, 2, 3, 4], state='readonly', width=28).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Login / Register", command=self._handle_login_register).grid(row=4, column=0, columnspan=2, pady=20)

    def _handle_login_register(self):
        email = self.email_entry.get().strip()
        name = self.name_entry.get().strip()
        selected_branch = self.branch_var.get()
        selected_year = self.year_var.get()

        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        student = conn.execute("SELECT * FROM student WHERE email=?", (email,)).fetchone()
        
        if student:
            self.current_email = email
            self._load_dashboard(dict(student))
        else:
            if not name: messagebox.showerror("Error", "Enter Name for registration."); conn.close(); return
            try:
                conn.execute("INSERT INTO student VALUES (NULL, ?, ?, ?, ?, 0.0, 0, 0)", 
                             (name, email, selected_branch, selected_year))
                conn.commit()
                self.current_email = email
                new_student_data = {'name': name, 'branch': selected_branch, 'year': selected_year, 'cgpa': 0.0, 'dsa_solved': 0, 'major_projects': 0}
                self._load_dashboard(new_student_data)
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {e}")
        conn.close()
        
        if self.current_email:
            self.notebook.tab(self.dashboard_tab, state='normal')
            self.notebook.select(self.dashboard_tab)

    def _setup_dashboard_tab(self):
        # Progress Form (Left)
        form_frame = ttk.LabelFrame(self.dashboard_tab, text="Update Progress", padding="10"); form_frame.pack(side='left', fill='y', padx=10, pady=10)
        self.entries = {}
        fields = {"CGPA (0.0-10.0):": 'cgpa', "DSA Solved (Goal: 150):": 'dsa_solved', "Projects Completed (Goal: 2):": 'major_projects'}
        for i, (label_text, key) in enumerate(fields.items()):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=20); entry.grid(row=i, column=1, padx=5, pady=5); self.entries[key] = entry
        ttk.Button(form_frame, text="Save & Get Guidance", command=self._save_progress).grid(row=len(fields), column=0, columnspan=2, pady=15)
        
        # Guidance Display (Right)
        guidance_frame = ttk.LabelFrame(self.dashboard_tab, text="Guidance", padding="10"); guidance_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.student_label = ttk.Label(guidance_frame, text="N/A", style='Header.TLabel'); self.student_label.pack(anchor='w', pady=5)
        self.summary_label = ttk.Label(guidance_frame, text="Login to view guidance.", wraplength=350, font=('Helvetica', 11, 'bold')); self.summary_label.pack(anchor='w', pady=10)
        self.guidance_listbox = tk.Listbox(guidance_frame, height=15, width=60, selectmode=tk.NONE, relief=tk.FLAT); self.guidance_listbox.pack(fill='both', expand=True)

    def _load_dashboard(self, student_data):
        self.student_label.config(text=f"Student: {student_data['name']}") 
        
        for key in self.entries.keys():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, str(student_data.get(key, 0)))
        self._update_guidance(student_data)

    def _save_progress(self):
        if not self.current_email: messagebox.showerror("Error", "Login first."); return
        try:
            cgpa = float(self.entries['cgpa'].get()); dsa = int(self.entries['dsa_solved'].get()); projects = int(self.entries['major_projects'].get())
            if not (0.0 <= cgpa <= 10.0 and dsa >= 0 and projects >= 0): raise ValueError("Invalid numbers.")
            
            conn = sqlite3.connect(DATABASE_NAME)
            conn.row_factory = sqlite3.Row
            conn.execute("UPDATE student SET cgpa=?, dsa_solved=?, major_projects=? WHERE email=?", (cgpa, dsa, projects, self.current_email))
            conn.commit()
            student_data = dict(conn.execute("SELECT * FROM student WHERE email=?", (self.current_email,)).fetchone())
            conn.close()
            self._update_guidance(student_data)
            messagebox.showinfo("Success", "Progress saved and guidance refreshed!")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def _update_guidance(self, student_data):
        summary, guidance_list = get_guidance(student_data)
        # Apply subtle color based on summary status
        summary_color = '#155724' if 'READY' in summary else '#856404' 
        summary_bg = '#d4edda' if 'READY' in summary else '#fff3cd' 

        self.summary_label.config(text=summary, foreground=summary_color, background=summary_bg, padding=5, relief=tk.RAISED)
        
        self.guidance_listbox.delete(0, tk.END)
        for item in guidance_list:
            self.guidance_listbox.insert(tk.END, item)

if __name__ == "__main__":
    app = SimpleVITTracker()
    app.mainloop()