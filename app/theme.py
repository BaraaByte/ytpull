"""Centralized ttk styling so the look stays consistent across the app."""
from tkinter import ttk


def apply_modern_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
    style.configure("TRadiobutton", font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Status.TLabel", font=("Segoe UI", 9))
    style.configure("Path.TLabel", font=("Consolas", 9))
    style.configure("Download.Horizontal.TProgressbar", thickness=18)
    return style
