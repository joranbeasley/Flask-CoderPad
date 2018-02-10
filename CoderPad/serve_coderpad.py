'''
simple script to serve coderpad
the first time its run it should prompt you for some setup info

'''
import os

import sys
import traceback

from CoderPad.configure import DoSetupCoderpadSite
from CoderPad.constants import CONFIG_FILE, DEFAULT_DB, load_config
from CoderPad.coderpad_socket_server.socket_server import socketio
from CoderPad.app import app
from CoderPad.models import User,db,init_app as db_init_app

def main():
    if not os.path.exists(CONFIG_FILE) and len(sys.argv)< 2:
        DoSetupCoderpadSite(['-w'])
    elif len(sys.argv)>1:
        DoSetupCoderpadSite()


    config = load_config(CONFIG_FILE)
    if not config.get('db_uri',None):
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
    if sys.version_info > (3,):
        socketio.run(app, config['host'], int(config['port']))
    else:
        socketio.run(app,config['host'].encode('latin1'),int(config['port'].encode('latin1')))


if __name__ == "__main__":
    main()