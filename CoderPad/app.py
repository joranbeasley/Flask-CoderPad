import os
from flask import Flask
# from flask_login import login_manager
from CoderPad.constants import STATIC_FOLDER, TEMPLATES_FOLDER
from CoderPad.filters import MyFilters
from CoderPad.coderpad_socket_server.socket_server import socketio
from CoderPad.views import flask_views
from CoderPad.views import api_views
from CoderPad.views.views_admin import admin_views

print("STATIC FOLDER:",STATIC_FOLDER)
print("TEMPLATE FOLDER:",TEMPLATES_FOLDER)
app = Flask(__name__,static_folder=STATIC_FOLDER,template_folder=TEMPLATES_FOLDER)
app.config['SECRET_KEY'] = 'secret!ShhHHHHH!!!@'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['debug'] = True
app.register_blueprint(flask_views)
app.register_blueprint(api_views,url_prefix="/api")
app.register_blueprint(admin_views,url_prefix="/admin")
socketio.init_app(app)
MyFilters.init_app(app)