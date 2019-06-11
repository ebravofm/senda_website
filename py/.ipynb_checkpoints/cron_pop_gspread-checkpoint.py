try:
    from .gspread_results import pop_X_gspread
except:
    from gspread_results import pop_X_gspread
import os


if __name__ == '__main__':
    pop_X_gspread()