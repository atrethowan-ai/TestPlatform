import unittest
import tkinter as tk
from quiz_pipeline.gui.app import QuizPipelineGUI

class QuizBuilderGUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QuizPipelineGUI()
        cls.app.update()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app = self.__class__.app
        self.app.notebook.select(1)
        self.tab = self.app.builder_tab
        self.tab.clear_editor()
        self.app.update()

    def test_load_template_button(self):
        self.tab.quiz_json_editor.delete(1.0, tk.END)
        self.tab.load_template_btn.invoke()
        text = self.tab.quiz_json_editor.get(1.0, tk.END)
        self.assertIn('"id"', text)
        self.assertIn('"sections"', text)
        status = self.tab.quiz_status_panel.get(1.0, tk.END)
        self.assertIn('Loaded quiz_authoring_template.json into editor', status)

    def test_clear_button(self):
        self.tab.quiz_json_editor.insert(tk.END, '{"foo": 1}')
        self.tab.clear_btn.invoke()
        text = self.tab.quiz_json_editor.get(1.0, tk.END)
        self.assertEqual(text.strip(), '')
        status = self.tab.quiz_status_panel.get(1.0, tk.END)
        self.assertIn('Editor cleared', status)

    def test_copy_json_button(self):
        self.tab.quiz_json_editor.insert(tk.END, '{"foo": 1}')
        self.tab.copy_json_btn.invoke()
        clipboard = self.app.clipboard_get()
        self.assertIn('foo', clipboard)
        status = self.tab.quiz_status_panel.get(1.0, tk.END)
        self.assertIn('Quiz JSON copied to clipboard', status)

    def test_validate_button_empty(self):
        self.tab.quiz_json_editor.delete(1.0, tk.END)
        self.tab.validate_btn.invoke()
        status = self.tab.quiz_status_panel.get(1.0, tk.END)
        self.assertIn('ERROR: Editor is empty', status)

    def test_validate_button_invalid_json(self):
        self.tab.quiz_json_editor.delete(1.0, tk.END)
        self.tab.quiz_json_editor.insert(tk.END, '{bad json}')
        self.tab.validate_btn.invoke()
        status = self.tab.quiz_status_panel.get(1.0, tk.END)
        self.assertIn('ERROR: JSON syntax error', status)

if __name__ == '__main__':
    unittest.main()
