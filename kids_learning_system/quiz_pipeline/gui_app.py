import os
import sys
import subprocess

# Ensure the src directory is on PYTHONPATH
SRC_PATH = os.path.join(os.path.dirname(__file__), 'src')
PYTHONPATH = os.environ.get('PYTHONPATH', '')
if SRC_PATH not in PYTHONPATH:
    os.environ['PYTHONPATH'] = SRC_PATH + os.pathsep + PYTHONPATH

# Launch the GUI as a module
cmd = [sys.executable, '-m', 'quiz_pipeline.gui.app']
subprocess.run(cmd, cwd=SRC_PATH)
