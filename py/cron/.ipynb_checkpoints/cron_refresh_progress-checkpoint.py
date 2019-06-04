try:
    from .progress_tools import update_progress
except:
    from progress_tools import update_progress
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    update_progress(json_path='../../static/data/progress.json')