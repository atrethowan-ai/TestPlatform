# Quiz Pipeline GUI settings for paths
import os

# Root directory for attempts (where attempt JSONs are stored)
here = os.path.abspath(os.path.dirname(__file__))
project_root = here
while not os.path.isdir(os.path.join(project_root, 'kids_learning_system')) and os.path.dirname(project_root) != project_root:
	project_root = os.path.dirname(project_root)
ATTEMPTS_DIR = os.path.join(project_root, 'kids_learning_system', 'quiz_pipeline', 'work', 'attempts')
# Root directory for quizzes (where quiz JSONs are stored)
QUIZZES_ROOT = os.path.join(project_root, 'kids_learning_system', 'content', 'quizzes')
