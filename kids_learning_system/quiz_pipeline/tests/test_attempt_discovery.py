
import os
import json
import glob
import sys
import unittest

# Add src to sys.path so quiz_pipeline can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from quiz_pipeline.services.discovery import AttemptDiscoveryService


class TestAttemptDiscoveryService(unittest.TestCase):
    def setUp(self):
        # Robust relative path: always resolve from project root
        here = os.path.abspath(os.path.dirname(__file__))
        # Go up to project root
        project_root = here
        while not os.path.isdir(os.path.join(project_root, 'kids_learning_system')) and os.path.dirname(project_root) != project_root:
            project_root = os.path.dirname(project_root)
        self.attempts_dir = os.path.join(project_root, 'kids_learning_system', 'quiz_pipeline', 'work', 'attempts')
        print(f"[DEBUG] Using attempts_dir: {self.attempts_dir}")
        print(f"[DEBUG] Files found: {list(glob.glob(os.path.join(self.attempts_dir, '**', '*.json'), recursive=True))}")
        self.child_id = 'test-user'

    def test_attempts_found_for_test_user(self):
        attempts = AttemptDiscoveryService.get_attempts_for_child(self.child_id, self.attempts_dir)
        print(f"Found attempts: {attempts}")
        self.assertTrue(isinstance(attempts, list))
        self.assertTrue(any(a['quizId'] for a in attempts), "No attempts found for test-user!")

    def test_attempts_have_required_fields(self):
        attempts = AttemptDiscoveryService.get_attempts_for_child(self.child_id, self.attempts_dir)
        for a in attempts:
            self.assertIn('id', a)
            self.assertIn('quizId', a)
            self.assertIn('startedAt', a)
            self.assertIn('completedAt', a)
            self.assertIn('path', a)

if __name__ == '__main__':
    unittest.main()
