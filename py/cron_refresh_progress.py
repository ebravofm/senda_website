try:
	from .update_progress import update_all
except:
	from update_progress import update_all
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
	update_all(json_path='../static/data/progress.json')