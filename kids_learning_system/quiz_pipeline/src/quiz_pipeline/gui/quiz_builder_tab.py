"""
quiz_builder_tab.py
Quiz Builder tab for the Quiz Pipeline GUI.
Encapsulates all layout, state and logic for creating / publishing quizzes from the GUI.
"""

import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from quiz_pipeline.services.validation_service import validate_authoring_quiz

# ---------------------------------------------------------------------------
# Path helpers (relative to this file's location inside src/quiz_pipeline/gui/)
# ---------------------------------------------------------------------------
_GUI_DIR = Path(__file__).resolve().parent          # …/src/quiz_pipeline/gui
_SRC_DIR = _GUI_DIR.parents[1]                      # …/src
_QUIZ_PIPELINE_ROOT = _GUI_DIR.parents[2]           # …/quiz_pipeline  (project root)
_TEMPLATES_DIR = _QUIZ_PIPELINE_ROOT / "templates"
_INCOMING_DIR = _QUIZ_PIPELINE_ROOT / "work" / "incoming"
_GENERATED_DIR = _QUIZ_PIPELINE_ROOT / "work" / "generated"


class QuizBuilderTab(tk.Frame):
    """
    A tk.Frame that provides the full Quiz Builder UI.
    Drop it into a ttk.Notebook as a tab.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self._build_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Row 0 – button bar
        btn_frame = tk.Frame(self, bd=1, relief=tk.GROOVE, padx=4, pady=4)
        btn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))

        buttons = [
            ("Load Template",         self.load_template,          "load_template_btn"),
            ("Validate",              self.validate,               "validate_btn"),
            ("Save to Incoming",      self.save_to_incoming,       "save_to_incoming_btn"),
            ("Build and Publish",     self.build_and_publish,      "build_and_publish_btn"),
            ("Clear",                 self.clear_editor,           "clear_btn"),
            ("Copy JSON",             self.copy_json,              "copy_json_btn"),
            ("Open Incoming Folder",  self.open_incoming_folder,   "open_incoming_btn"),
            ("Open Generated Folder", self.open_generated_folder,  "open_generated_btn"),
        ]
        for col, (label, cmd, attr_name) in enumerate(buttons):
            b = tk.Button(btn_frame, text=label, command=cmd, padx=6)
            b.grid(row=0, column=col, padx=3, pady=2, sticky="w")
            setattr(self, attr_name, b)

        # Row 1 left – JSON editor
        editor_frame = tk.LabelFrame(self, text="Quiz Authoring JSON")
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        self.editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.NONE, font=("Consolas", 10),
            undo=True, autoseparators=True
        )
        self.editor.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.quiz_json_editor = self.editor

        # Row 1 right – status / validation panel
        status_frame = tk.LabelFrame(self, text="Validation / Status")
        status_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=4)
        status_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        self.status_panel = scrolledtext.ScrolledText(
            status_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled",
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white"
        )
        self.status_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.quiz_status_panel = self.status_panel

        # Configure text tags for coloured output
        self.status_panel.tag_configure("error",   foreground="#f48771")
        self.status_panel.tag_configure("warning", foreground="#cca700")
        self.status_panel.tag_configure("info",    foreground="#9cdcfe")
        self.status_panel.tag_configure("success", foreground="#4ec994")
        self.status_panel.tag_configure("normal",  foreground="#d4d4d4")

        # Row 2 – metadata preview
        meta_frame = tk.LabelFrame(self, text="Quiz Metadata Preview")
        meta_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 8))
        self.metadata_label = tk.Label(
            meta_frame, text="", anchor="w", justify="left",
            font=("Consolas", 10), fg="#555555"
        )
        self.metadata_label.grid(row=0, column=0, sticky="w", padx=6, pady=4)

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def _clear_status(self):
        self.status_panel.config(state="normal")
        self.status_panel.delete(1.0, tk.END)
        self.status_panel.config(state="disabled")

    def _append_status(self, line: str, tag: str = "normal"):
        self.status_panel.config(state="normal")
        self.status_panel.insert(tk.END, line + "\n", tag)
        self.status_panel.see(tk.END)
        self.status_panel.config(state="disabled")

    def _set_status(self, msg: str):
        """Replace the whole status panel with msg, auto-colouring lines."""
        self._clear_status()
        for line in msg.splitlines():
            if line.startswith("ERROR"):
                tag = "error"
            elif line.startswith("WARNING"):
                tag = "warning"
            elif line.startswith("INFO"):
                tag = "info"
            elif line.startswith("SUCCESS"):
                tag = "success"
            else:
                tag = "normal"
            self._append_status(line, tag)

    def _get_status(self) -> str:
        return self.status_panel.get(1.0, tk.END)

    # ------------------------------------------------------------------
    # Internal validation helper (returns errors, warnings; updates UI)
    # ------------------------------------------------------------------

    def _run_validation(self) -> tuple:
        """Parse JSON and validate. Updates status panel and metadata. Returns (errors, warnings, quiz_or_None)."""
        self._clear_status()
        self.metadata_label.config(text="")

        raw = self.editor.get(1.0, tk.END)
        if not raw.strip():
            self._append_status("ERROR: Editor is empty.", "error")
            return [], [], None

        # Step 1 – JSON syntax
        try:
            quiz = json.loads(raw)
        except json.JSONDecodeError as exc:
            self._append_status(f"ERROR: JSON syntax error — {exc}", "error")
            return ["JSON syntax"], [], None

        # Step 2 – Schema / authoring validation
        errors, warnings = validate_authoring_quiz(quiz)

        # Step 3 – Update metadata preview
        if isinstance(quiz, dict):
            sections = quiz.get("sections", [])
            q_count = sum(len(s.get("questions", [])) for s in sections if isinstance(s, dict))
            q_types = sorted({
                q.get("type", "?")
                for s in sections if isinstance(s, dict)
                for q in s.get("questions", []) if isinstance(q, dict)
            })
            meta = (
                f"id:             {quiz.get('id', '')}\n"
                f"title:          {quiz.get('title', '')}\n"
                f"ageGroup:       {quiz.get('ageGroup', '')}\n"
                f"question count: {q_count}\n"
                f"question types: {', '.join(q_types)}"
            )
            self.metadata_label.config(text=meta)

        # Step 4 – Render results
        if errors or warnings:
            for e in errors:
                self._append_status(f"ERROR: {e}", "error")
            for w in warnings:
                tag = "info" if w.startswith("INFO") else "warning"
                self._append_status(w, tag)
        else:
            self._append_status("INFO: Validation passed. Quiz is ready to publish.", "info")

        return errors, warnings, quiz

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def load_template(self):
        template_path = _TEMPLATES_DIR / "quiz_authoring_template.json"
        try:
            text = template_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self._set_status(f"ERROR: Template not found: {template_path}")
            return
        except Exception as exc:
            self._set_status(f"ERROR: Could not read template: {exc}")
            return
        self.editor.delete(1.0, tk.END)
        self.editor.insert(tk.END, text)
        self._set_status("INFO: Loaded quiz_authoring_template.json into editor.")

    def validate(self):
        self._run_validation()

    def save_to_incoming(self):
        errors, warnings, quiz = self._run_validation()
        if errors:
            self._append_status("ERROR: Cannot save — fix validation errors first.", "error")
            return
        if quiz is None:
            return

        quiz_id = quiz.get("id", "").strip()
        if not quiz_id:
            self._append_status("ERROR: Quiz 'id' is missing or empty.", "error")
            return

        _INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _INCOMING_DIR / f"{quiz_id}.json"

        if out_path.exists():
            if not messagebox.askyesno(
                "Overwrite?",
                f"'{out_path.name}' already exists in incoming/.\nOverwrite?"
            ):
                self._append_status("INFO: Save cancelled by user.", "info")
                return

        raw = self.editor.get(1.0, tk.END).strip()
        out_path.write_text(raw, encoding="utf-8")
        self._append_status(f"INFO: Saved → {out_path}", "info")

    def build_and_publish(self):
        errors, warnings, quiz = self._run_validation()
        if errors:
            self._append_status("ERROR: Cannot build — fix validation errors first.", "error")
            return
        if quiz is None:
            return

        quiz_id = quiz.get("id", "").strip()
        if not quiz_id:
            self._append_status("ERROR: Quiz 'id' is missing or empty.", "error")
            return

        # Auto-save to incoming so the CLI can find it
        _INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        in_path = _INCOMING_DIR / f"{quiz_id}.json"
        raw = self.editor.get(1.0, tk.END).strip()
        in_path.write_text(raw, encoding="utf-8")

        cmd = [sys.executable, "-m", "quiz_pipeline.cli.main", "build-package", "--input", str(in_path)]
        self._append_status(f"INFO: Running build-package…", "info")
        self._append_status(f"INFO: cwd={_SRC_DIR}", "info")
        self.update_idletasks()  # flush UI before blocking subprocess

        try:
            result = subprocess.run(
                cmd,
                cwd=str(_SRC_DIR),
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            self._append_status("ERROR: Build timed out after 5 minutes.", "error")
            return
        except Exception as exc:
            self._append_status(f"ERROR: Failed to start build process: {exc}", "error")
            return

        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                self._append_status(line, "normal")
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines():
                tag = "error" if result.returncode != 0 else "warning"
                self._append_status(line, tag)

        if result.returncode == 0:
            self._append_status("SUCCESS: Build and publish complete.", "success")
            # Show where files landed
            generated_quiz_dir = _GENERATED_DIR / quiz_id
            if generated_quiz_dir.exists():
                self._append_status(f"INFO: Generated output → {generated_quiz_dir}", "info")
        else:
            self._append_status(f"ERROR: Build failed (exit code {result.returncode}).", "error")

    def clear_editor(self):
        self.editor.delete(1.0, tk.END)
        self._clear_status()
        self.metadata_label.config(text="")
        self._append_status("INFO: Editor cleared.", "info")

    def copy_json(self):
        text = self.editor.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        self._set_status("INFO: Quiz JSON copied to clipboard.")

    def open_incoming_folder(self):
        _INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{_INCOMING_DIR}"')

    def open_generated_folder(self):
        _GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{_GENERATED_DIR}"')
