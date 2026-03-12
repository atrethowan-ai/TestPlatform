import os
import json
glob = __import__('glob')

# --- Child Discovery ---
class ChildDiscoveryService:
    @staticmethod
    def get_children():
        # Static for now, can be extended to load from config or DB
        return [
            {'id': 'forrest', 'name': 'Forrest'},
            {'id': 'homie', 'name': 'Homie'},
            {'id': 'test-user', 'name': 'Test User'}
        ]

# --- Attempt Discovery ---
class AttemptDiscoveryService:
    @staticmethod
    def get_attempts_for_child(child_id, attempts_dir):
        print(f"[DIAG] AttemptDiscoveryService: attempts_dir = {attempts_dir}")
        files = glob.glob(os.path.join(attempts_dir, '**', '*.json'), recursive=True)
        print(f"[DIAG] AttemptDiscoveryService: files found = {files}")
        attempts = []
        for path in files:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                file_child_id = data.get('childId')
                file_quiz_id = data.get('quizId')
                print(f"[DIAG] File: {path}\n  childId: {file_child_id}\n  quizId: {file_quiz_id}")
                if file_child_id == child_id:
                    attempt_id = data.get('id') or data.get('attemptId')
                    started_at = data.get('startedAt') or data.get('completedAt')
                    attempts.append({
                        'id': attempt_id,
                        'quizId': file_quiz_id,
                        'startedAt': started_at,
                        'completedAt': data.get('completedAt'),
                        'path': path
                    })
                else:
                    print(f"[DIAG] Skipping file (childId mismatch): {file_child_id} != {child_id}")
            except Exception as e:
                print(f"[DIAG] Error reading {path}: {e}")
                continue
        print(f"[DIAG] Attempts matching childId '{child_id}': {attempts}")
        attempts.sort(key=lambda x: x.get('startedAt', ''), reverse=True)
        return attempts

# --- Quiz Resolution ---
class QuizResolutionService:
    @staticmethod
    def find_quiz_file(quiz_id, quizzes_root):
        # Search all quiz files in quizzes_root/age6 and quizzes_root/age9
        for age_dir in ['age6', 'age9']:
            dir_path = os.path.join(quizzes_root, age_dir)
            if not os.path.isdir(dir_path):
                continue
            for fname in os.listdir(dir_path):
                if fname.endswith('.json'):
                    fpath = os.path.join(dir_path, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        # Accept either 'id' or 'quizId' as key
                        if data.get('id') == quiz_id or data.get('quizId') == quiz_id:
                            return fpath
                    except Exception:
                        continue
        return None
