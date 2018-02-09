from flask import Flask
# from flask_login import login_manager

from filters import MyFilters
from models import db,login_manager
from socket_server import socketio
from views import flask_views
from api import api
from views_admin import admin_views

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!ShhHHHHH!!!@'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['debug'] = True
app.register_blueprint(flask_views)
app.register_blueprint(api,url_prefix="/api")
app.register_blueprint(admin_views,url_prefix="/admin")
socketio.init_app(app)
MyFilters.init_app(app)