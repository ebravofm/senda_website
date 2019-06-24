try:
    from .gspread_results import pop_X_gspread
except:
    from gspread_results import pop_X_gspread
import os


try:
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
except:
	pass


if __name__ == '__main__':
    pop_X_gspread()