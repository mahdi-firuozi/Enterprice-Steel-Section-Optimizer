import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import json
import os
import threading
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- COMPLETE STEEL SECTION DATABASE ---
STEEL_DATABASE = {
    "IPE Series": {
        "IPE 80": {"h": 80, "bf": 46, "tw": 3.8, "tf": 5.2},
        "IPE 100": {"h": 100, "bf": 55, "tw": 4.1, "tf": 5.7},
        "IPE 120": {"h": 120, "bf": 64, "tw": 4.4, "tf": 6.3},
        "IPE 140": {"h": 140, "bf": 73, "tw": 4.7, "tf": 6.9},
        "IPE 160": {"h": 160, "bf": 82, "tw": 5.0, "tf": 7.4},
        "IPE 180": {"h": 180, "bf": 91, "tw": 5.3, "tf": 8.0},
        "IPE 200": {"h": 200, "bf": 100, "tw": 5.6, "tf": 8.5},
        "IPE 220": {"h": 220, "bf": 110, "tw": 5.9, "tf": 9.2},
        "IPE 240": {"h": 240, "bf": 120, "tw": 6.2, "tf": 9.8},
        "IPE 270": {"h": 270, "bf": 135, "tw": 6.6, "tf": 10.2},
        "IPE 300": {"h": 300, "bf": 150, "tw": 7.1, "tf": 10.7},
        "IPE 330": {"h": 330, "bf": 160, "tw": 7.5, "tf": 11.5},
        "IPE 360": {"h": 360, "bf": 170, "tw": 8.0, "tf": 12.7},
        "IPE 400": {"h": 400, "bf": 180, "tw": 8.6, "tf": 13.5},
        "IPE 450": {"h": 450, "bf": 190, "tw": 9.4, "tf": 14.6},
        "IPE 500": {"h": 500, "bf": 200, "tw": 10.2, "tf": 16.0},
        "IPE 550": {"h": 550, "bf": 210, "tw": 11.1, "tf": 17.2},
        "IPE 600": {"h": 600, "bf": 220, "tw": 12.0, "tf": 19.0}
    },
    "HEB Series": {
        "HEB 100": {"h": 100, "bf": 100, "tw": 6.0, "tf": 10.0},
        "HEB 120": {"h": 120, "bf": 120, "tw": 6.5, "tf": 11.0},
        "HEB 140": {"h": 140, "bf": 140, "tw": 7.0, "tf": 12.0},
        "HEB 160": {"h": 160, "bf": 160, "tw": 8.0, "tf": 13.0},
        "HEB 180": {"h": 180, "bf": 180, "tw": 8.5, "tf": 14.0},
        "HEB 200": {"h": 200, "bf": 200, "tw": 9.0, "tf": 15.0},
        "HEB 240": {"h": 240, "bf": 240, "tw": 10.0, "tf": 17.0},
        "HEB 300": {"h": 300, "bf": 300, "tw": 11.0, "tf": 19.0},
        "HEB 400": {"h": 400, "bf": 300, "tw": 13.5, "tf": 24.0},
        "HEB 500": {"h": 500, "bf": 300, "tw": 14.5, "tf": 28.0},
        "HEB 600": {"h": 600, "bf": 300, "tw": 15.5, "tf": 30.0}
    },
    "HEA Series": {
        "HEA 100": {"h": 96, "bf": 100, "tw": 5.0, "tf": 8.0},
        "HEA 120": {"h": 114, "bf": 120, "tw": 5.0, "tf": 8.0},
        "HEA 140": {"h": 133, "bf": 140, "tw": 5.5, "tf": 8.5},
        "HEA 160": {"h": 152, "bf": 160, "tw": 6.0, "tf": 9.0},
        "HEA 180": {"h": 171, "bf": 180, "tw": 6.0, "tf": 9.5},
        "HEA 200": {"h": 190, "bf": 200, "tw": 6.5, "tf": 10.0},
        "HEA 240": {"h": 230, "bf": 240, "tw": 7.5, "tf": 12.0},
        "HEA 300": {"h": 290, "bf": 300, "tw": 8.5, "tf": 14.0},
        "HEA 400": {"h": 390, "bf": 300, "tw": 11.0, "tf": 19.0},
        "HEA 600": {"h": 590, "bf": 300, "tw": 13.0, "tf": 25.0}
    },
    "IPN / INP Series": {
        "IPN 80": {"h": 80, "bf": 42, "tw": 3.9, "tf": 5.9},
        "IPN 100": {"h": 100, "bf": 50, "tw": 4.5, "tf": 6.8},
        "IPN 120": {"h": 120, "bf": 58, "tw": 5.1, "tf": 7.7},
        "IPN 140": {"h": 140, "bf": 66, "tw": 5.7, "tf": 8.6},
        "IPN 160": {"h": 160, "bf": 74, "tw": 6.3, "tf": 9.5},
        "IPN 180": {"h": 180, "bf": 82, "tw": 6.9, "tf": 10.4},
        "IPN 200": {"h": 200, "bf": 90, "tw": 7.5, "tf": 11.3},
        "IPN 300": {"h": 300, "bf": 125, "tw": 10.8, "tf": 16.2},
        "IPN 400": {"h": 400, "bf": 155, "tw": 14.4, "tf": 21.6},
        "IPN 600": {"h": 600, "bf": 215, "tw": 21.6, "tf": 32.4}
    }
}

class HelpToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        
    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = ctk.CTkLabel(tw, text=self.text, fg_color=("#2c3e50", "#1a252f"), text_color="white", corner_radius=4, padx=6, pady=4, font=("Arial", 11))
        lbl.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()

class EngineeringCore:
    @staticmethod
    def analyze_section(h, tw, bf, tf, unit_system="mm"):
        scale_map = {"mm": 1.0, "cm": 10.0, "m": 1000.0}
        scale = scale_map.get(unit_system, 1.0)
        h_mm, tw_mm, bf_mm, tf_mm = h * scale, tw * scale, bf * scale, tf * scale
        
        if h_mm <= 0 or tw_mm <= 0 or bf_mm <= 0 or tf_mm <= 0:
            return {"Valid": False, "Error": "Dimensions must be positive."}
        if (2 * tf_mm) >= h_mm or tw_mm >= bf_mm:
            return {"Valid": False, "Error": "Geometric incompatibility."}

        hw_mm = h_mm - (2 * tf_mm)
        A_bot = bf_mm * tf_mm
        y_bot = tf_mm / 2.0
        A_web = tw_mm * hw_mm
        y_web = tf_mm + (hw_mm / 2.0)
        A_top = bf_mm * tf_mm
        y_top = h_mm - (tf_mm / 2.0)
        
        A_total = A_bot + A_web + A_top
        y_bar = (A_bot*y_bot + A_web*y_web + A_top*y_top) / A_total
        x_bar = bf_mm / 2.0
        pna_y = h_mm / 2.0  # Double symmetric I-section standard

        Ix = (bf_mm*tf_mm**3/12 + A_bot*(y_bot-y_bar)**2) + \
             (tw_mm*hw_mm**3/12 + A_web*(y_web-y_bar)**2) + \
             (bf_mm*tf_mm**3/12 + A_top*(y_top-y_bar)**2)
             
        Iy = (2 * tf_mm * bf_mm**3 / 12.0) + (hw_mm * tw_mm**3 / 12.0)
        Sx, Sy = Ix / max(y_bar, h_mm - y_bar), Iy / (bf_mm / 2.0)
        rx, ry = np.sqrt(Ix / A_total), np.sqrt(Iy / A_total)
        weight = A_total * 7.85e-6 * 1000.0
        
        Zx = (bf_mm * tf_mm * (h_mm - tf_mm)) + (tw_mm * hw_mm**2 / 4.0)
        Zy = (2 * tf_mm * (bf_mm**2) / 4.0) + (hw_mm * (tw_mm**2) / 4.0)

        u1, u2, u3, u4 = 1.0/scale, 1.0/(scale**2), 1.0/(scale**3), 1.0/(scale**4)

        return {
            "Valid": True, "Area": A_total * u2, "Weight": weight,
            "Ix": Ix * u4, "Iy": Iy * u4, "Sx": Sx * u3, "Sy": Sy * u3,
            "rx": rx * u1, "ry": ry * u1, "Zx": Zx * u3, "Zy": Zy * u3,
            "y_bar": y_bar * u1, "x_bar": x_bar * u1, "PNA_y": pna_y * u1,
            "Shape_Factor": Zx / Sx if Sx > 0 else 0, "Efficiency": Ix / (weight * 1000) if weight > 0 else 0
        }

class DashboardLayoutMixin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_mode = "Dark"
        ctk.set_appearance_mode(self.theme_mode)
        self.comparison_matrix_stack = []
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.create_sidebar()
        self.create_workspace()

    def create_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=290, corner_radius=0, fg_color=("#f8f9fa", "#1a1c1e"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="STEEL PRO", font=("Consolas", 26, "bold"), text_color=("#2b3e50", "#3498db")).pack(pady=(15, 2))
        ctk.CTkLabel(self.sidebar, text="Enterprise Edition V3", font=("Arial", 11), text_color="gray").pack(pady=(0, 15))
        
        ctk.CTkLabel(self.sidebar, text="System Units", font=("Arial", 11, "bold")).pack(padx=15, anchor="w")
        self.unit_var = ctk.StringVar(value="mm")
        self.unit_menu = ctk.CTkOptionMenu(self.sidebar, values=["mm", "cm", "m"], variable=self.unit_var, command=self.unit_changed_callback)
        self.unit_menu.pack(padx=15, pady=5, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="Database Selection", font=("Arial", 11, "bold")).pack(padx=15, anchor="w", pady=(10, 0))
        self.db_group_var = ctk.StringVar(value="IPE Series")
        self.db_group_menu = ctk.CTkOptionMenu(self.sidebar, values=list(STEEL_DATABASE.keys()), variable=self.db_group_var, command=self.populate_profile_dropdown)
        self.db_group_menu.pack(padx=15, pady=5, fill="x")
        
        self.profile_var = ctk.StringVar(value="Select Profile...")
        self.profile_menu = ctk.CTkOptionMenu(self.sidebar, values=[], variable=self.profile_var, command=self.load_selected_database_profile)
        self.profile_menu.pack(padx=15, pady=5, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="Enterprise Tools", font=("Arial", 11, "bold")).pack(padx=15, anchor="w", pady=(15, 0))
        actions = [
            ("💾 Save Workspace", self.save_project_json),
            ("📂 Load Workspace", self.load_project_json),
            ("📄 Enterprise PDF Report", self.trigger_pdf_export),
            ("📊 Advanced Excel Workbook", self.trigger_excel_export),
            ("⚖️ Add to Compare Table", self.append_to_comparison),
            ("🚀 Multi-Obj Optimizer", self.open_optimization_wizard)
        ]
        for text, cmd in actions:
            btn = ctk.CTkButton(self.sidebar, text=text, command=cmd, anchor="w", fg_color="transparent", border_width=1, text_color=("#2c3e50", "#ffffff"))
            btn.pack(padx=15, pady=3, fill="x")
            
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Theme Mode", command=self.toggle_ui_theme_state)
        self.theme_switch.select()
        self.theme_switch.pack(padx=15, pady=20, anchor="w")

    def create_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.workspace.grid_columnconfigure(0, weight=3)
        self.workspace.grid_columnconfigure(1, weight=4)
        self.workspace.grid_rowconfigure(1, weight=1)
        self.workspace.grid_rowconfigure(2, weight=0)
        
        # Upper KPI Section
        self.kpi_master_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.kpi_master_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.kpi_widgets = {}
        target_kpis = [("Area", "#3498db"), ("Weight", "#2ecc71"), ("Ix", "#9b59b6"), ("Efficiency", "#f1c40f")]
        
        for idx, (title, color) in enumerate(target_kpis):
            self.kpi_master_frame.grid_columnconfigure(idx, weight=1)
            card = ctk.CTkFrame(self.kpi_master_frame, fg_color=("#ffffff", "#242424"), height=75, corner_radius=6, border_width=1, border_color=("#e0e0e0", "#333333"))
            card.grid(row=0, column=idx, padx=4, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkFrame(card, width=4, fg_color=color).pack(side="left", fill="y")
            lbl_val = ctk.CTkLabel(card, text="0.00", font=("Consolas", 18, "bold"))
            lbl_val.pack(padx=8, pady=(8, 0), anchor="w")
            lbl_tit = ctk.CTkLabel(card, text=title, font=("Arial", 10, "bold"), text_color="gray")
            lbl_tit.pack(padx=8, pady=(0, 8), anchor="w")
            self.kpi_widgets[title] = lbl_val

        self.control_panel_frame = ctk.CTkScrollableFrame(self.workspace, label_text="Parametric Inputs & Matrix")
        self.control_panel_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        self.graphic_panel_frame = ctk.CTkFrame(self.workspace, corner_radius=8, border_width=1, border_color=("#e0e0e0", "#333333"))
        self.graphic_panel_frame.grid(row=1, column=1, sticky="nsew")
        
        # --- FIXED TREEVIEW TREE (LIVE COMPARISON MATRIX) ---
        self.compare_panel = ctk.CTkFrame(self.workspace, height=160, corner_radius=8, border_width=1, border_color=("#e0e0e0", "#333333"))
        self.compare_panel.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        top_bar = ctk.CTkFrame(self.compare_panel, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(top_bar, text="Live Comparison Matrix Table", font=("Arial", 11, "bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="Clear Selected Row", width=120, height=22, font=("Arial", 10), fg_color="#e74c3c", hover_color="#c0392b", command=self.clear_selected_matrix_row).pack(side="right")
        
        # Explicitly configure visibility styling for Dark Mode compatibility
        self.tree_scroll = ttk.Scrollbar(self.compare_panel)
        self.tree_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        self.tree = ttk.Treeview(self.compare_panel, columns=("Profile", "Area", "Weight", "Ix", "Eff"), show="headings", height=4, yscrollcommand=self.tree_scroll.set)
        self.tree.pack(fill="both", expand=True, padx=(10, 0), pady=5)
        self.tree_scroll.config(command=self.tree.yview)
        
        for col, w in zip(self.tree["columns"], [160, 90, 90, 110, 90]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
            
        # Re-apply structural UI colors to the Treeview widget
        self.apply_treeview_styles()

    def apply_treeview_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        bg_col = "#242424" if self.theme_mode == "Dark" else "#ffffff"
        fg_col = "#ffffff" if self.theme_mode == "Dark" else "#000000"
        style.configure("Treeview", background=bg_col, foreground=fg_col, fieldbackground=bg_col, rowheight=24, font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#333333" if self.theme_mode == "Dark" else "#e0e0e0", foreground=fg_col, font=("Arial", 10, "bold"))
        style.map('Treeview', background=[('selected', '#3498db')], foreground=[('selected', 'white')])

    def toggle_ui_theme_state(self):
        self.theme_mode = "Dark" if self.theme_switch.get() == 1 else "Light"
        ctk.set_appearance_mode(self.theme_mode)
        self.apply_treeview_styles()
        self.force_instant_recalculation()

class LiveEngineAndPlotterMixin(DashboardLayoutMixin):
    def initialize_live_system(self):
        self.input_fields = {}
        self.debounce_lock_timer = None
        self.computed_cache_results = {"Valid": False}
        self.inline_errors = {}
        
        inputs = [("Web Height (h)", "h"), ("Web Thick (tw)", "tw"), ("Flange Width (bf)", "bf"), ("Flange Thick (tf)", "tf")]
        
        for label, key in inputs:
            row = ctk.CTkFrame(self.control_panel_frame, fg_color="transparent")
            row.pack(fill="x", pady=3, padx=10)
            ctk.CTkLabel(row, text=label, font=("Arial", 11, "bold")).pack(side="left")
            entry = ctk.CTkEntry(row, width=85, justify="center")
            entry.pack(side="right")
            entry.bind("<KeyRelease>", self.intercept_input_stream)
            self.input_fields[key] = entry
            
            err_lbl = ctk.CTkLabel(self.control_panel_frame, text="", text_color="#e74c3c", font=("Arial", 9), height=10)
            err_lbl.pack(fill="x", padx=10)
            self.inline_errors[key] = err_lbl
            
        self.results_table_host = ctk.CTkFrame(self.control_panel_frame, fg_color="transparent")
        self.results_table_host.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.plot_figure, self.plot_axis = plt.subplots(facecolor='none', figsize=(4.8, 4.8))
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.graphic_panel_frame)
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def intercept_input_stream(self, event=None):
        if self.debounce_lock_timer: self.after_cancel(self.debounce_lock_timer)
        self.debounce_lock_timer = self.after(200, self.dispatch_computation_thread)

    def dispatch_computation_thread(self):
        threading.Thread(target=self.execute_safe_computation_pipeline, daemon=True).start()

    def execute_safe_computation_pipeline(self):
        vals = {}
        valid = True
        border_valid, border_invalid = ("#2ecc71", "#27ae60"), ("#e74c3c", "#c0392b")
        
        for key, ent in self.input_fields.items():
            try:
                v = float(ent.get())
                if v <= 0: raise ValueError
                vals[key] = v
                self.after(0, lambda e=ent, k=key: (e.configure(border_color=border_valid), self.inline_errors[k].configure(text="")))
            except:
                valid = False
                self.after(0, lambda e=ent, k=key: (e.configure(border_color=border_invalid), self.inline_errors[k].configure(text="Must be > 0")))
                
        if not valid: return
            
        analysis = EngineeringCore.analyze_section(vals['h'], vals['tw'], vals['bf'], vals['tf'], self.unit_var.get())
        if analysis["Valid"]:
            self.computed_cache_results = analysis
            self.after(0, lambda: self.render_refreshed_ui_state(vals))
        else:
            self.after(0, lambda err=analysis["Error"]: self.inline_errors['h'].configure(text=err))

    def render_refreshed_ui_state(self, geometry):
        res = self.computed_cache_results
        self.kpi_widgets["Area"].configure(text=f"{res['Area']:,.1f}")
        self.kpi_widgets["Weight"].configure(text=f"{res['Weight']:,.1f}")
        self.kpi_widgets["Ix"].configure(text=f"{res['Ix']:,.1f}")
        self.kpi_widgets["Efficiency"].configure(text=f"{res['Efficiency']:,.2f}")
        
        for c in self.results_table_host.winfo_children(): c.destroy()
        for k, v in res.items():
            if k in ["Valid", "Error"]: continue
            row = ctk.CTkFrame(self.results_table_host, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=k, font=("Arial", 10), text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=f"{v:,.2f}", font=("Consolas", 11, "bold")).pack(side="right")
            
        self.draw_closed_vector_section(geometry['h'], geometry['tw'], geometry['bf'], geometry['tf'], res['x_bar'], res['y_bar'], res['PNA_y'])

    def draw_closed_vector_section(self, h, tw, bf, tf, x_bar, y_bar, pna_y):
        self.plot_axis.clear()
        
        # --- FIXED GEOMETRIC SEQUENCE LOGIC (PERFECT HOURGLASS CONTUOR COORDS) ---
        # Origin centered horizontally, matching y_bar center of coordinates natively
        x_coords = [
            -bf/2,  bf/2,                  # Top rim edge line
            bf/2,   tw/2,                  # Top flange right underside lip
            tw/2,   tw/2,                  # Vertical web outer right boundary
            bf/2,   bf/2,                  # Bottom flange right upper lip
            -bf/2, -bf/2,                  # Bottom base baseline edge
            -tw/2, -tw/2,                  # Vertical web outer left boundary
            -bf/2, -bf/2,                  # Top flange left underside lip
            -bf/2                          # Back to terminal loop start
        ]
        y_coords = [
            h - y_bar, h - y_bar,          # Top plate surface
            h - y_bar - tf, h - y_bar - tf,# Drop down into top flange underside
            h - y_bar - tf,  -y_bar + tf,  # Moving through the inner column channel
            -y_bar + tf,    -y_bar,        # Down outer baseline lip
            -y_bar,         -y_bar + tf,   # Flat bottom edge plate
            -y_bar + tf,    h - y_bar - tf,# Rising up left web boundary wall
            h - y_bar - tf, h - y_bar,     # Inner step back up to the ceiling
            h - y_bar                      # Target sealing execution closure
        ]
        
        theme_col = "white" if self.theme_mode == "Dark" else "black"
        self.plot_axis.fill(x_coords, y_coords, color='#2980b9', alpha=0.75, ec='#1f6aa5', lw=2.5, label='Molded Steel Profile')
        
        # Crosshair alignment markers matching true structural engineering notation
        self.plot_axis.plot(0, 0, color='#e74c3c', marker='+', ms=12, mew=2, label=f"Centroid (X:{x_bar:.1f}, Y:{y_bar:.1f})")
        self.plot_axis.axhline(pna_y - y_bar, color='#f1c40f', ls='--', lw=1.5, label="PNA Axis Location")
        
        self.plot_axis.set_aspect('equal', adjustable='datalim')
        self.plot_axis.grid(True, ls=':', alpha=0.4, color='gray')
        self.plot_axis.legend(loc="upper right", fontsize=8)
        self.plot_axis.set_title(f"CAD Profile Cross-Section View", color=theme_col, pad=10, fontname="Consolas", weight="bold")
        self.plot_axis.tick_params(colors=theme_col, labelsize=8)
        for spine in self.plot_axis.spines.values(): spine.set_edgecolor(theme_col)
            
        self.plot_figure.tight_layout()
        self.plot_canvas.draw()

class LogicAndOptimizerMixin(LiveEngineAndPlotterMixin):
    def populate_profile_dropdown(self, event=None):
        grp = self.db_group_var.get()
        profiles = list(STEEL_DATABASE.get(grp, {}).keys())
        self.profile_menu.configure(values=profiles)
        if profiles:
            self.profile_var.set(profiles[0])
            self.load_selected_database_profile(profiles[0])

    def load_selected_database_profile(self, name):
        grp = self.db_group_var.get()
        if name in STEEL_DATABASE.get(grp, {}):
            data = STEEL_DATABASE[grp][name]
            for k, ent in self.input_fields.items():
                ent.delete(0, 'end')
                ent.insert(0, str(data[k]))
            self.force_instant_recalculation()

    def unit_changed_callback(self, val): self.force_instant_recalculation()
    def force_instant_recalculation(self): self.dispatch_computation_thread()

    # --- FIXED COMPARISON SYNC INTERFACE ---
    def append_to_comparison(self):
        if self.computed_cache_results.get("Valid"):
            prof = f"{self.db_group_var.get()} - {self.profile_var.get()}"
            res = self.computed_cache_results
            entry = (prof, f"{res['Area']:.1f}", f"{res['Weight']:.1f}", f"{res['Ix']:.1f}", f"{res['Efficiency']:.2f}")
            
            # Direct runtime insertion inside Tkinter Treeview widget frame
            self.tree.insert("", "end", values=entry)
            self.comparison_matrix_stack.append(entry)

    def clear_selected_matrix_row(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            vals = self.tree.item(item)['values']
            # Flush out match item index inside stack cache array
            self.comparison_matrix_stack = [x for x in self.comparison_matrix_stack if x[0] != vals[0]]
            self.tree.delete(item)

    def open_optimization_wizard(self):
        wiz = ctk.CTkToplevel(self)
        wiz.title("Multi-Objective Optimization Matrix")
        wiz.geometry("440x360")
        wiz.transient(self)
        wiz.grab_set()
        
        ctk.CTkLabel(wiz, text="Required Minimum Target Ix (Moment of Inertia):", font=("Arial", 11, "bold")).pack(pady=8)
        ix_ent = ctk.CTkEntry(wiz, justify="center")
        ix_ent.insert(0, "15000000")
        ix_ent.pack(pady=4)
        
        def run_opt():
            try: req_ix = float(ix_ent.get())
            except: return
            candidates = []
            for grp, profs in STEEL_DATABASE.items():
                for name, dims in profs.items():
                    res = EngineeringCore.analyze_section(**dims, unit_system="mm")
                    if res["Valid"] and res["Ix"] >= req_ix:
                        candidates.append({"Profile": name, "Group": grp, "Weight": res["Weight"], "Eff": res["Efficiency"], "Ix": res["Ix"]})
            
            # Multi-Objective Pareto sorting layer
            candidates.sort(key=lambda x: (x["Weight"], -x["Eff"]))
            top_5 = candidates[:5]
            
            res_frame = ctk.CTkScrollableFrame(wiz, height=180, label_text="Top 5 Best Performing Matches")
            res_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            if not top_5:
                ctk.CTkLabel(res_frame, text="No compliant options found.").pack()
            else:
                for idx, c in enumerate(top_5):
                    txt = f"#{idx+1} {c['Profile']} [Weight: {c['Weight']:.1f} kg/m | Eff: {c['Eff']:.1f}]"
                    btn = ctk.CTkButton(res_frame, text=txt, command=lambda g=c['Group'], p=c['Profile']: (self.db_group_var.set(g), self.populate_profile_dropdown(), self.profile_var.set(p), self.load_selected_database_profile(p), wiz.destroy()))
                    btn.pack(fill="x", pady=2)
                    
        ctk.CTkButton(wiz, text="Execute Objective Search Logic", fg_color="#2ecc71", hover_color="#27ae60", command=run_opt).pack(pady=8)

    def save_project_json(self):
        if not self.computed_cache_results.get("Valid"): return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Workspace JSON", "*.json")])
        if path:
            data = {"unit": self.unit_var.get(), "db_group": self.db_group_var.get(), "profile_name": self.profile_var.get(), "inputs": {k: box.get() for k, box in self.input_fields.items()}}
            with open(path, 'w') as fh: json.dump(data, fh, indent=4)

    def load_project_json(self):
        path = filedialog.askopenfilename(filetypes=[("Workspace JSON", "*.json")])
        if path:
            with open(path, 'r') as fh: data = json.load(fh)
            self.unit_var.set(data.get("unit", "mm"))
            self.db_group_var.set(data.get("db_group", "IPE Series"))
            self.populate_profile_dropdown()
            self.profile_var.set(data.get("profile_name", "IPE 80"))
            for k, val in data["inputs"].items():
                self.input_fields[k].delete(0, 'end')
                self.input_fields[k].insert(0, str(val))
            self.force_instant_recalculation()

    def trigger_pdf_export(self):
        if not self.computed_cache_results.get("Valid"): return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Engineering PDF", "*.pdf")])
        if not path: return
        img_buf = BytesIO()
        self.plot_figure.savefig(img_buf, format='png', dpi=180, facecolor='white')
        img_buf.seek(0)
        doc = SimpleDocTemplate(path, pagesize=A4)
        story, styles = [], getSampleStyleSheet()
        story.append(Paragraph("Enterprise Structural Section Report", styles['Heading1']))
        story.append(Spacer(1, 12))
        table_data = [["Property Parameter", f"Calculated Metric Output ({self.unit_var.get()})"]]
        for k, v in self.computed_cache_results.items():
            if k in ["Valid", "Error"]: continue
            table_data.append([k, f"{v:,.2f}" if isinstance(v, float) else str(v)])
        t = Table(table_data, colWidths=[200, 180])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 1, colors.grey), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#ecf0f1')])]))
        story.extend([t, Spacer(1, 15), Image(img_buf, width=320, height=320)])
        doc.build(story)
        messagebox.showinfo("Export Success", "Report Compiled.")

    def trigger_excel_export(self):
        if not self.computed_cache_results.get("Valid"): return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Sheet", "*.xlsx")])
        if not path: return
        with pd.ExcelWriter(path) as writer:
            df_res = pd.DataFrame(list(self.computed_cache_results.items()), columns=["Property", "Value"])
            df_res.to_excel(writer, sheet_name="Dashboard", index=False)
            if self.comparison_matrix_stack:
                df_comp = pd.DataFrame(self.comparison_matrix_stack, columns=["Profile", "Area", "Weight", "Ix", "Efficiency"])
                df_comp.to_excel(writer, sheet_name="Comparison Log Matrix", index=False)
        messagebox.showinfo("Export Success", "Workbook Saved.")

# --- APPLICATION EXECUTIVE SUITE APPLICATION ENTRY POINT ---
class SteelProEnterpriseApp(LogicAndOptimizerMixin):
    def __init__(self):
        super().__init__()
        self.initialize_live_system()
        self.populate_profile_dropdown()
        self.title("Steel Section Calculator Pro - Enterprise V3")
        self.geometry("1240x820")
        self.minsize(1050, 720)
        
        # Load default safe baseline index profile configuration
        self.profile_var.set("IPE 140")
        self.load_selected_database_profile("IPE 140")

if __name__ == "__main__":
    app = SteelProEnterpriseApp()
    app.mainloop()
