import os

import sys

from CoderPad.constants import CONFIG_FILE, DEFAULT_DB
from CoderPad.coderpad_socket_server.socket_server import socketio
from CoderPad.app import app
from CoderPad.models import User,db,init_app as db_init_app
def load_config(fpath):
    return dict([x.strip() for x in line.split("=")] for line in open(fpath,'rb') if "=" in line)

if not os.path.exists(CONFIG_FILE):

    db_uri = raw_input("Enter Database URI(%s):"%DEFAULT_DB)
    db_user = db_password = db_database_name=""
    if not db_uri:db_uri=DEFAULT_DB
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
else:
    config = load_config(CONFIG_FILE)
    app.config['SQLALCHEMY_DATABASE_URI'] = config['db_uri']
db_init_app(app)
try:
    users = User.query.all()
except:
    print("CREATING DATABASE...")
    db.create_all()
    users = User.query.all()
if not users or "--create-admin" in sys.argv:
    admin_username=raw_input("Admin Username:")
    admin_password=raw_input("Password:")
    admin_email=raw_input("Admin Email(admin@coderpad.demo):")
    u = User.get_or_create(admin_username,admin_password,admin_username,admin_email,is_admin=True)
    u.is_admin = True
    db.session.commit()
if not os.path.exists(CONFIG_FILE):
    host = raw_input("Host To Serve on (0.0.0.0):")
    if not host:host="0.0.0.0"
    port = raw_input("Port to serve on (8000):")
    if not port:port = "8000"
    with open(CONFIG_FILE,"wb") as f:
        f.write("host=%s\n"%host)
        f.write("port=%s\n"%port)
        f.write("db_uri=%s\n"%db_uri)

# print User.query.all()


if __name__ == '__main__':
    config = load_config(CONFIG_FILE)

    print("Serving on %s:%s"%(config['host'],config['port']))
    print("NOTE that you can change your config settings at %s"%CONFIG_FILE)
    print("NOTE that your can run this with the `--create-admin` flag to create a new admin user")
    socketio.run(app,config['host'],config['port'])

