from os import path
import sys

# Script location
try:
    SCRIPT_DIR = path.dirname(path.realpath(__file__))
except Exception as ex:
    SCRIPT_DIR = sys.path[0]

APIKEY_FILE_PATH = path.join(SCRIPT_DIR, '..', 'apikey.txt')

ESCAPE_CHAR = '\\'

# Largo máximo de nombres de variable de usuario
MAX_VARIABLE_NAME_LEN = 45
VARIABLE_CONTENT_PREVIEW = 60

# Place to put saved variables files
DUMPS_PATH = path.join(SCRIPT_DIR, 'var_dumps')
SAVED_SESSIONS_PATH = path.join(DUMPS_PATH, 'saved_sessions')

PROMPT = 'ARKAN>'
