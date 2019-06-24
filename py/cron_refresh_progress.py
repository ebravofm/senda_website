try:
    from .progress_tools import update_qualtrics_progress
except:
    from progress_tools import update_qualtrics_progress
import os


try:
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
except:
	pass


if __name__ == '__main__':
    update_qualtrics_progress(json_path='../static/data/progress.json')