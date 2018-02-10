import os

import sys
import traceback

from CoderPad.constants import CONFIG_FILE, DEFAULT_DB, load_config
from CoderPad.coderpad_socket_server.socket_server import socketio
from CoderPad.app import app
from CoderPad.models import User,db,init_app as db_init_app
from setup_server import DoSetupCoderpadSite, ask_yesno

if not os.path.exists(CONFIG_FILE) and len(sys.argv)< 2:
    DoSetupCoderpadSite(['-w'])
elif len(sys.argv)>1:
    DoSetupCoderpadSite()
if __name__ == '__main__':
    config = load_config(CONFIG_FILE)
    if 'db_uri' not in config:
        sys.stderr.write("ERROR: No Database found please run `setup-coderpad --wizard`\n")
        sys.exit(-1)
    app.config['SQLALCHEMY_DATABASE_URI'] = config['db_uri']
    db_init_app(app)
    try:
        results = User.query.all()
    except:
        traceback.print_exc()
        sys.stderr.write("ERROR: Inproperly Configured database! you should run `setup-coderpad --wizard`\n")
        sys.exit(-1)
    if not results:
        sys.stderr.write("ERROR: You do not appear to have any admin users... please run `setup-coderpad --add-admin-user\n`")
        sys.exit(-1)
    if not config['stmp_server']:
        sys.stderr.write("WARNING: STMP not setup, you will not be able to send emails... please run `setup-coderpad --configure-stmp`\n")
    print("Serving on %s:%s"%(config['host'],config['port']))
    print("NOTE that you can change your config settings at %s"%CONFIG_FILE)
    print("NOTE that your can run this with the `--create-admin` flag to create a new admin user")
    socketio.run(app,config['host'],config['port'])

