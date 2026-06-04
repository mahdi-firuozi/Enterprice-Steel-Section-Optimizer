# Enterprise Steel Section Calculator & Optimizer (v3)

An enterprise-grade civil engineering desktop application built with Python. This tool integrates comprehensive structural steel profile databases (like the IPE series) with real-time engineering calculations, dynamic charts, and executive reporting tools.

## 🚀 Key Features
* Modern UI: Built using CustomTkinter for a sleek, responsive, and dark-mode friendly enterprise interface.
* Engineering Analytics: Real-time property extraction (height, flange width, thickness) and efficiency calculations for steel profiles.
* Live Visualizations: Embedded Matplotlib graphs inside the GUI showing structural beam profiles dynamically.
* Advanced Reporting: High-fidelity, multi-page PDF generation (via ReportLab) with corporate styling, custom data tables, and automated Excel logging sheets using Pandas.
* Clean Architecture: Utilizes robust Python design patterns, cross-inheritance mixins, and local caching to prevent UI lagging during multi-threaded calculations.

## 🛠️ Tech Stack
* GUI Framework: CustomTkinter (Modern Tkinter wrapper)
* Data & Analytics: Pandas, NumPy
* Data Visualization: Matplotlib (Agg backend integration)
* Reporting Engine: ReportLab (PDF compiler), OpenPyXL
