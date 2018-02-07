import hashlib
import json
import traceback

from flask import Blueprint, request
from flask_login import current_user, login_required

from models import User, Invitations, Room, db

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


@api.route("/token/<s>")
@login_required
def create_token(s):
    # r = request
    if not current_user.is_admin:
        return s
    return hashlib.sha256(s).hexdigest()


@api.route("/invite",methods=["POST"])
@login_required
def invite_guest():
    # r = request
    if not current_user.is_admin:
        return "Not Authorized"
    room_id = request.form['room_id']
    email_address = request.form['email']
    room = Room.query.get(room_id)
    invite_code = create_token(room.room_name+email_address)
    new_invite = Invitations(email_address=email_address,room=room,invite_code=invite_code)
    db.session.add(new_invite)
    db.session.commit()
    return json.dumps(new_invite.to_dict())