import os

# Redis
PASTES_DATA_QUEUE = "pastes_data"
PASTES_TO_ANALIZE_QUEUE = "pastes_to_analyze"
STORER_QUEUE = 'storer'

# Paste data fields
PD_KEY = 'key'

# Paths
METADATA_SUFFIX = ".metadata"


# Logger
cwd  = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(cwd, 'log.txt')
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOGGER_NAME = "mylog"

# Hacks
WEIRD_PH = "&%&"

# General
SECONDS_TO_WAIT = 180

# Conditions keywords
STRING =  "string"
REGEX =  "regex"
MULTILINE = "multiline"
FLAGS = "flags"
NAME = "name"

# Storer actions
ACTION_STORER_DELETE = "delete"
ACTION_STORER_STORE = "store"