try:
    from .responses_tools import dump_responses
except:
    from responses_tools import dump_responses
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    dump_responses(response_folder='../../static/data/responses')