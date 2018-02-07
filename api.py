import json
import traceback

from flask import Blueprint, request
from flask_login import current_user

from models import User

api = Blueprint('api', __name__)

@api.route("/login",methods=["POST"])
def do_login():
    username = request.form.get('username','')
    password = request.form.get('password','')
    user = User.login(username, password)
    if not user:
        return json.dumps({'user':None})
    else:
        return json.dumps({'user':user.to_dict()})

@api.route("/me")
def me():
    try:
        return json.dumps({'user':current_user.to_dict()})
    except:
        traceback.print_exc()
        return json.dumps({'user':None})


