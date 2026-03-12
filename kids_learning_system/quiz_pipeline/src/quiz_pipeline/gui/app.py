
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os

# Support both module and script execution
try:
    from quiz_pipeline.extract.attempt_loader import load_attempts
    from quiz_pipeline.extract.attempt_summariser import summarise_attempts
    from quiz_pipeline.prompts.prompt_builder import build_prompt
    from quiz_pipeline.services.discovery import ChildDiscoveryService, AttemptDiscoveryService, QuizResolutionService
    from quiz_pipeline.config.gui_paths import ATTEMPTS_DIR, QUIZZES_ROOT
except ImportError:
    from extract.attempt_loader import load_attempts
    from extract.attempt_summariser import summarise_attempts
    from prompts.prompt_builder import build_prompt
    from services.discovery import ChildDiscoveryService, AttemptDiscoveryService, QuizResolutionService
    from config.gui_paths import ATTEMPTS_DIR, QUIZZES_ROOT


class QuizPipelineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Pipeline - Summarise Child")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Main layout: left controls, right results
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Controls panel (left)
        controls = tk.Frame(self)
        controls.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        # Child dropdown
        tk.Label(controls, text="Child:").grid(row=0, column=0, sticky="w", pady=5)
        self.child_var = tk.StringVar()
        self.child_dropdown = ttk.Combobox(controls, textvariable=self.child_var, state="readonly", width=25)
        self.child_dropdown.grid(row=0, column=1, pady=5)
        self.child_dropdown.bind("<<ComboboxSelected>>", self.on_child_selected)

        # Attempt dropdown
        tk.Label(controls, text="Attempt:").grid(row=1, column=0, sticky="w", pady=5)
        self.attempt_var = tk.StringVar()
        self.attempt_dropdown = ttk.Combobox(controls, textvariable=self.attempt_var, state="readonly", width=40)
        self.attempt_dropdown.grid(row=1, column=1, pady=5)
        self.attempt_dropdown.bind("<<ComboboxSelected>>", self.on_attempt_selected)

        # Generate Summary Button
        self.generate_btn = tk.Button(controls, text="Generate Summary", command=self.generate_summary, width=20)
        self.generate_btn.grid(row=2, column=1, pady=15, sticky="w")

        # Copy to Clipboard Button
        self.copy_btn = tk.Button(controls, text="Copy to Clipboard", command=self.copy_to_clipboard, width=20)
        self.copy_btn.grid(row=3, column=1, pady=5, sticky="w")

        # Advanced section (collapsible)
        self.advanced_frame = tk.LabelFrame(controls, text="Advanced (Manual Override)")
        self.advanced_frame.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")
        self.advanced_frame.grid_remove()
        self.advanced_visible = False
        self.manual_attempt_path = tk.StringVar()
        self.manual_quiz_path = tk.StringVar()
        tk.Label(self.advanced_frame, text="Attempts File:").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(self.advanced_frame, textvariable=self.manual_attempt_path, width=30).grid(row=0, column=1, pady=2)
        tk.Button(self.advanced_frame, text="Browse", command=self.browse_attempt_file).grid(row=0, column=2, padx=2)
        tk.Label(self.advanced_frame, text="Quiz File:").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(self.advanced_frame, textvariable=self.manual_quiz_path, width=30).grid(row=1, column=1, pady=2)
        tk.Button(self.advanced_frame, text="Browse", command=self.browse_quiz_file).grid(row=1, column=2, padx=2)
        self.advanced_toggle_btn = tk.Button(controls, text="Show Advanced", command=self.toggle_advanced)
        self.advanced_toggle_btn.grid(row=5, column=1, sticky="w")

        # Results panel (right)
        results_panel = tk.Frame(self)
        results_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        results_panel.rowconfigure(0, weight=1)
        results_panel.columnconfigure(0, weight=1)
        tk.Label(results_panel, text="Results:").grid(row=0, column=0, sticky="nw")
        self.output_text = scrolledtext.ScrolledText(results_panel, width=80, height=30, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, sticky="nsew")

        # Populate child dropdown
        self.child_map = {c['name']: c['id'] for c in ChildDiscoveryService.get_children()}
        self.child_dropdown['values'] = list(self.child_map.keys())
        self.child_dropdown.set('')
        self.attempt_dropdown.set('')
        self.attempts_for_child = []
        self.selected_attempt = None

    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.grid_remove()
            self.advanced_toggle_btn.config(text="Show Advanced")
        else:
            self.advanced_frame.grid()
            self.advanced_toggle_btn.config(text="Hide Advanced")
        self.advanced_visible = not self.advanced_visible

    def on_child_selected(self, event=None):
        child_name = self.child_var.get()
        child_id = self.child_map.get(child_name)
        self.attempts_for_child = AttemptDiscoveryService.get_attempts_for_child(child_id, ATTEMPTS_DIR)
        if not self.attempts_for_child:
            self.attempt_dropdown['values'] = []
            self.attempt_dropdown.set('')
            self.selected_attempt = None
            return
        labels = [f"{a['startedAt']} | {a['quizId']} | {a['id']}" for a in self.attempts_for_child]
        self.attempt_dropdown['values'] = labels
        self.attempt_dropdown.set(labels[0])
        self.selected_attempt = self.attempts_for_child[0]

    def on_attempt_selected(self, event=None):
        idx = self.attempt_dropdown.current()
        if idx >= 0 and idx < len(self.attempts_for_child):
            self.selected_attempt = self.attempts_for_child[idx]
        else:
            self.selected_attempt = None

    def browse_attempt_file(self):
        filename = tk.filedialog.askopenfilename(title="Select Attempt Export JSON", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.manual_attempt_path.set(filename)

    def browse_quiz_file(self):
        filename = tk.filedialog.askopenfilename(title="Select Quiz JSON", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.manual_quiz_path.set(filename)

    def generate_summary(self):
        # Advanced/manual override
        if self.advanced_visible and self.manual_attempt_path.get() and self.manual_quiz_path.get():
            attempt_path = self.manual_attempt_path.get()
            quiz_path = self.manual_quiz_path.get()
            try:
                attempt = load_attempts(attempt_path)
                with open(quiz_path, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                summary = summarise_attempts(attempt, quiz_data)
                self.display_summary(summary, quiz_data)
            except Exception as e:
                self.display_error(f"Failed to generate summary: {e}")
            return

        # Normal workflow
        if not self.selected_attempt:
            self.display_error("Please select a child and attempt.")
            return
        attempt_path = self.selected_attempt['path']
        try:
            attempt = load_attempts(attempt_path)
        except Exception as e:
            self.display_error(f"Failed to load attempt: {e}")
            return
        quiz_id = attempt.get('quizId')
        quiz_path = QuizResolutionService.find_quiz_file(quiz_id, QUIZZES_ROOT)
        if not quiz_path:
            self.display_error(f"Could not resolve quiz file for quizId: {quiz_id}")
            return
        try:
            with open(quiz_path, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            summary = summarise_attempts(attempt, quiz_data)
            self.display_summary(summary, quiz_data)
        except Exception as e:
            self.display_error(f"Failed to generate summary: {e}")

    def display_summary(self, summary, quiz=None):
        readable = []
        # Human-readable summary
        readable.append("=== Human-Readable Summary ===\n")
        readable.append(build_prompt(summary, quiz))
        # JSON summary
        readable.append("\n=== JSON Summary ===")
        readable.append(json.dumps(summary, indent=2))
        # LLM prompt block (same as above for now)
        readable.append("\n=== LLM Prompt Block ===")
        readable.append(build_prompt(summary, quiz))
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, '\n'.join(readable))

    def display_error(self, msg):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"ERROR: {msg}")

    def copy_to_clipboard(self):
        output = self.output_text.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(output)
        messagebox.showinfo("Copied", "Output copied to clipboard.")

import sys
if __name__ == "__main__":
    app = QuizPipelineGUI()
    def _on_close():
        app.quit()
        app.destroy()
        sys.exit(0)
    app.protocol("WM_DELETE_WINDOW", _on_close)
    app.mainloop()

    def browse_attempt_file(self):
        filename = filedialog.askopenfilename(title="Select Attempt Export JSON", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.attempt_file_entry.delete(0, tk.END)
            self.attempt_file_entry.insert(0, filename)

    def browse_quiz_file(self):
        filename = filedialog.askopenfilename(title="Select Quiz JSON", filetypes=[("JSON Files", "*.json")])
        if filename:
            self.quiz_file_entry.delete(0, tk.END)
            self.quiz_file_entry.insert(0, filename)

    def generate_summary(self):
        child_id = self.child_id_entry.get().strip()
        attempt_path = self.attempt_file_entry.get().strip()
        quiz_path = self.quiz_file_entry.get().strip()
        if not child_id or not attempt_path or not quiz_path:
            messagebox.showerror("Missing Input", "Please provide Child ID, Attempts file, and Quiz file.")
            return
        try:
            attempt = load_attempts(attempt_path)
            with open(quiz_path, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            summary = summarise_attempts(attempt, quiz_data)
            self.display_summary(summary)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {e}")

    def copy_to_clipboard(self):
        output = self.output_text.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(output)
        messagebox.showinfo("Copied", "Output copied to clipboard.")

if __name__ == "__main__":
    app = QuizPipelineGUI()
    app.mainloop()
