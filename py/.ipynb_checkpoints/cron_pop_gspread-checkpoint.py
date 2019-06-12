try:
    from .gspread_results import pop_X_gspread
except:
    from gspread_results import pop_X_gspread
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    pop_X_gspread()