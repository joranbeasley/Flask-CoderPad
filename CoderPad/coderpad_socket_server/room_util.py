import json
import os
from threading import Lock
from CoderPad.constants import CONFIG_DIR



file_lock = Lock()
def get_program_path(room_name):
    base_path =os.path.join(CONFIG_DIR,'sessions')
    # if not os.path.exists(base_path):
    try:
        os.makedirs(base_path)
    except (IOError, Exception):
        pass
    return os.path.join(base_path,'%s.program'%room_name)
def get_progam_stat(room_name):
    return os.stat(get_program_path(room_name))
def get_latest_prog(room_name):
    cache_file = get_program_path(room_name)
    if not os.path.exists(cache_file):
        open(cache_file,'wb').close()
    return open(cache_file,"rb").read().decode('latin1')
def update_latest_prog(room,prog_text):
    file_lock.acquire()
    cache_file = get_program_path(room)
    with open(cache_file,"wb") as f:
        # f.seek(0)
        f.write(prog_text.encode("latin1"))
    file_lock.release()

def get_room_data(room_name):
    raise NotImplemented()
def room_active(room_name):
    return get_room_data(room_name).get('active',False)

    # with open(get_room_meta_path(payload['room_name']),"wb") as f:
    #     json.dump(payload,f)
