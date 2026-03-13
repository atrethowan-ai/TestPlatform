"""
app.py
Quiz Pipeline GUI — main application window.
Tabs:
  1. Summary  — generate child performance summaries from attempt exports
  2. Quiz Builder — create, validate and publish new quizzes without touching the filesystem
"""

import json
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

try:
    from quiz_pipeline.extract.attempt_loader import load_attempts
    from quiz_pipeline.extract.attempt_summariser import summarise_attempts
    from quiz_pipeline.gui.quiz_builder_tab import QuizBuilderTab
    from quiz_pipeline.prompts.prompt_builder import build_prompt
    from quiz_pipeline.services.discovery import (
        AttemptDiscoveryService,
        ChildDiscoveryService,
        QuizResolutionService,
    )
    from quiz_pipeline.config.gui_paths import ATTEMPTS_DIR, QUIZZES_ROOT
except ImportError:
    from extract.attempt_loader import load_attempts
    from extract.attempt_summariser import summarise_attempts
    from gui.quiz_builder_tab import QuizBuilderTab
    from prompts.prompt_builder import build_prompt
    from services.discovery import (
        AttemptDiscoveryService,
        ChildDiscoveryService,
        QuizResolutionService,
    )
    from config.gui_paths import ATTEMPTS_DIR, QUIZZES_ROOT


class QuizPipelineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Pipeline")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        notebook = ttk.Notebook(self)
        self.notebook = ttk.Notebook(self)
        notebook = self.notebook
        notebook.pack(fill="both", expand=True)

        # Tab 1 – Summary
        summary_tab = tk.Frame(notebook)
        notebook.add(summary_tab, text="Summary")
        self._build_summary_tab(summary_tab)

        # Tab 2 – Quiz Builder
        builder_tab = QuizBuilderTab(notebook)
        self.builder_tab = builder_tab
        notebook.add(self.builder_tab, text="Quiz Builder")

    # ------------------------------------------------------------------
    # Summary tab layout
    # ------------------------------------------------------------------

    def _build_summary_tab(self, parent: tk.Frame):
        parent.columnconfigure(0, weight=0)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        controls = tk.Frame(parent)
        controls.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        tk.Label(controls, text="Child:").grid(row=0, column=0, sticky="w", pady=5)
        self.child_var = tk.StringVar()
        self.child_dropdown = ttk.Combobox(controls, textvariable=self.child_var, state="readonly", width=25)
        self.child_dropdown.grid(row=0, column=1, pady=5)
        self.child_dropdown.bind("<<ComboboxSelected>>", self._on_child_selected)

        tk.Label(controls, text="Attempt:").grid(row=1, column=0, sticky="w", pady=5)
        self.attempt_var = tk.StringVar()
        self.attempt_dropdown = ttk.Combobox(controls, textvariable=self.attempt_var, state="readonly", width=40)
        self.attempt_dropdown.grid(row=1, column=1, pady=5)
        self.attempt_dropdown.bind("<<ComboboxSelected>>", self._on_attempt_selected)

        tk.Button(controls, text="Generate Summary", command=self._generate_summary, width=20).grid(
            row=2, column=1, pady=15, sticky="w"
        )
        tk.Button(controls, text="Copy to Clipboard", command=self._copy_to_clipboard, width=20).grid(
            row=3, column=1, pady=5, sticky="w"
        )

        self._advanced_visible = False
        self._manual_attempt_path = tk.StringVar()
        self._manual_quiz_path = tk.StringVar()
        self._advanced_frame = tk.LabelFrame(controls, text="Advanced (Manual Override)")
        self._advanced_frame.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")
        self._advanced_frame.grid_remove()
        tk.Label(self._advanced_frame, text="Attempts File:").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(self._advanced_frame, textvariable=self._manual_attempt_path, width=30).grid(row=0, column=1, pady=2)
        tk.Button(self._advanced_frame, text="Browse", command=self._browse_attempt_file).grid(row=0, column=2, padx=2)
        tk.Label(self._advanced_frame, text="Quiz File:").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(self._advanced_frame, textvariable=self._manual_quiz_path, width=30).grid(row=1, column=1, pady=2)
        tk.Button(self._advanced_frame, text="Browse", command=self._browse_quiz_file).grid(row=1, column=2, padx=2)
        self._advanced_toggle_btn = tk.Button(controls, text="Show Advanced", command=self._toggle_advanced)
        self._advanced_toggle_btn.grid(row=5, column=1, sticky="w")

        results_panel = tk.Frame(parent)
        results_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        results_panel.rowconfigure(1, weight=1)
        results_panel.columnconfigure(0, weight=1)
        tk.Label(results_panel, text="Results:").grid(row=0, column=0, sticky="nw")
        self.output_text = scrolledtext.ScrolledText(results_panel, width=80, height=30, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, sticky="nsew")

        self._child_map = {c["name"]: c["id"] for c in ChildDiscoveryService.get_children()}
        self.child_dropdown["values"] = list(self._child_map.keys())
        self.child_dropdown.set("")
        self.attempt_dropdown.set("")
        self._attempts_for_child = []
        self._selected_attempt = None

    # ------------------------------------------------------------------
    # Summary tab events
    # ------------------------------------------------------------------

    def _toggle_advanced(self):
        if self._advanced_visible:
            self._advanced_frame.grid_remove()
            self._advanced_toggle_btn.config(text="Show Advanced")
        else:
            self._advanced_frame.grid()
            self._advanced_toggle_btn.config(text="Hide Advanced")
        self._advanced_visible = not self._advanced_visible

    def _on_child_selected(self, _event=None):
        child_name = self.child_var.get()
        child_id = self._child_map.get(child_name)
        self._attempts_for_child = AttemptDiscoveryService.get_attempts_for_child(child_id, ATTEMPTS_DIR)
        if not self._attempts_for_child:
            self.attempt_dropdown["values"] = []
            self.attempt_dropdown.set("")
            self._selected_attempt = None
            return
        labels = [f"{a['startedAt']} | {a['quizId']} | {a['id']}" for a in self._attempts_for_child]
        self.attempt_dropdown["values"] = labels
        self.attempt_dropdown.set(labels[0])
        self._selected_attempt = self._attempts_for_child[0]

    def _on_attempt_selected(self, _event=None):
        idx = self.attempt_dropdown.current()
        if 0 <= idx < len(self._attempts_for_child):
            self._selected_attempt = self._attempts_for_child[idx]
        else:
            self._selected_attempt = None

    def _browse_attempt_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Select Attempt Export JSON", filetypes=[("JSON Files", "*.json")])
        if path:
            self._manual_attempt_path.set(path)

    def _browse_quiz_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Select Quiz JSON", filetypes=[("JSON Files", "*.json")])
        if path:
            self._manual_quiz_path.set(path)

    def _generate_summary(self):
        if self._advanced_visible and self._manual_attempt_path.get() and self._manual_quiz_path.get():
            try:
                attempt = load_attempts(self._manual_attempt_path.get())
                with open(self._manual_quiz_path.get(), "r", encoding="utf-8") as fh:
                    quiz_data = json.load(fh)
                summary = summarise_attempts(attempt, quiz_data)
                self._display_summary(summary, quiz_data)
            except Exception as exc:
                self._display_error(f"Failed to generate summary: {exc}")
            return

        if not self._selected_attempt:
            self._display_error("Please select a child and attempt.")
            return

        try:
            attempt = load_attempts(self._selected_attempt["path"])
        except Exception as exc:
            self._display_error(f"Failed to load attempt: {exc}")
            return

        quiz_id = attempt.get("quizId")
        quiz_path = QuizResolutionService.find_quiz_file(quiz_id, QUIZZES_ROOT)
        if not quiz_path:
            self._display_error(f"Could not resolve quiz file for quizId: {quiz_id}")
            return

        try:
            with open(quiz_path, "r", encoding="utf-8") as fh:
                quiz_data = json.load(fh)
            summary = summarise_attempts(attempt, quiz_data)
            self._display_summary(summary, quiz_data)
        except Exception as exc:
            self._display_error(f"Failed to generate summary: {exc}")

    def _display_summary(self, summary, quiz=None):
        parts = [
            "=== Human-Readable Summary ===\n",
            build_prompt(summary, quiz),
            "\n=== JSON Summary ===",
            json.dumps(summary, indent=2),
            "\n=== LLM Prompt Block ===",
            build_prompt(summary, quiz),
        ]
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "\n".join(parts))

    def _display_error(self, msg: str):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"ERROR: {msg}")

    def _copy_to_clipboard(self):
        output = self.output_text.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(output)
        messagebox.showinfo("Copied", "Output copied to clipboard.")


if __name__ == "__main__":
    app = QuizPipelineGUI()

    def _on_close():
        app.quit()
        app.destroy()
        sys.exit(0)

    app.protocol("WM_DELETE_WINDOW", _on_close)
    app.mainloop()
