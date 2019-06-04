try:
    from .responses_tools import dump_responses
except:
    from responses_tools import dump_responses
import os


if __name__ == '__main__':
    dump_responses()