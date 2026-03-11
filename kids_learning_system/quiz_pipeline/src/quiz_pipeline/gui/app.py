import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import json
import os

# Support both module and script execution
try:
    from quiz_pipeline.extract.attempt_loader import load_attempts
    from quiz_pipeline.extract.attempt_summariser import summarise_attempts
    from quiz_pipeline.prompts.prompt_builder import build_prompt
except ImportError:    
    from extract.attempt_loader import load_attempts
    from extract.attempt_summariser import summarise_attempts
    from prompts.prompt_builder import build_prompt

class QuizPipelineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Pipeline - Summarise Child")
        self.geometry("700x500")

        # Child ID
        tk.Label(self, text="Child ID:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.child_id_entry = tk.Entry(self, width=30)
        self.child_id_entry.grid(row=0, column=1, padx=10, pady=5)

        # Attempt file
        tk.Label(self, text="Attempts File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.attempt_file_entry = tk.Entry(self, width=40)
        self.attempt_file_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self, text="Browse", command=self.browse_attempt_file).grid(row=1, column=2, padx=5, pady=5)

        # Quiz file
        tk.Label(self, text="Quiz File:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.quiz_file_entry = tk.Entry(self, width=40)
        self.quiz_file_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self, text="Browse", command=self.browse_quiz_file).grid(row=2, column=2, padx=5, pady=5)

        # Generate Summary Button
        tk.Button(self, text="Generate Summary", command=self.generate_summary).grid(row=3, column=1, pady=10)

        # Copy to Clipboard Button
        tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=3, column=2, pady=10)

        # Output Text Area
        tk.Label(self, text="Output:").grid(row=4, column=0, sticky="nw", padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(self, width=80, height=20)
        self.output_text.grid(row=4, column=1, columnspan=2, padx=10, pady=5)

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
            readable = []
            for domain, stats in summary['domainStats'].items():
                readable.append(f"Domain: {domain} | Correct: {stats['correct']} | Incorrect: {stats['incorrect']} | Total: {stats['total']}")
            weak = ', '.join(summary['weakDomains']) or 'None'
            readable.append(f"\nWeak Domains: {weak}\n")
            readable.append("=== JSON Summary ===")
            readable.append(json.dumps(summary, indent=2))
            readable.append("\n=== LLM Prompt ===")
            readable.append(build_prompt(summary))
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, '\n'.join(readable))
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
