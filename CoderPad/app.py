from flask import Flask
# from flask_login import login_manager

from filters import MyFilters
from CoderPad.coderpad_socket_server.socket_server import socketio
from .views import flask_views
from .views import api_views
from .views.views_admin import admin_views

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!ShhHHHHH!!!@'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['debug'] = True
app.register_blueprint(flask_views)
app.register_blueprint(api_views,url_prefix="/api")
app.register_blueprint(admin_views,url_prefix="/admin")
socketio.init_app(app)
MyFilters.init_app(app)