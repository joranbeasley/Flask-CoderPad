import os
CONFIG_DIR = os.path.join(os.path.expanduser("~"),".coderpad.d")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
CONFIG_FILE = os.path.join(CONFIG_DIR,".coderpad.ini")
DEFAULT_DB_PATH  = os.path.join(CONFIG_DIR,".coderpad.db").replace("\\","/")#.replace(":","")
DEFAULT_DB = "sqlite:///"+DEFAULT_DB_PATH
