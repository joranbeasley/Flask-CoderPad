import os
import traceback
from collections import OrderedDict

import sys

CONFIG_DIR = os.path.join(os.path.expanduser("~"),".coderpad.d")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
CONFIG_FILE = os.path.join(CONFIG_DIR,".coderpad.ini")
DEFAULT_DB_PATH  = os.path.join(CONFIG_DIR,".coderpad.db").replace("\\","/")#.replace(":","")
DEFAULT_DB = "sqlite:///"+DEFAULT_DB_PATH


def load_config(fpath=CONFIG_FILE):
    try:
        return OrderedDict([x.strip().replace("\\n","\n") for x in line.decode('latin1').split("=")] for line in open(fpath,'rb') if b"=" in line)
    except:
        traceback.print_exc()
        return OrderedDict.fromkeys('host port db_uri prompt stmp_server stmp_username stmp_password'.split())

def save_config(configItems,fpath=CONFIG_FILE):
    if isinstance(configItems,(list,tuple)):
        configItems = OrderedDict(configItems)
    if not isinstance(configItems,dict):
        raise TypeError("Expecting an ordered dict!")
    if not isinstance(configItems,OrderedDict):
        sys.stderr.write("WARNING: OrderedDicts are advised for save_config")
    with open(fpath,"wb") as f:
        for key,value in configItems.items():
            f.write("{key}={value}\n".format(key=key,value=value))
    print("Configuration Saved To {fpath}".format(fpath=fpath))
