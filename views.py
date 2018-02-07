import os
from flask import Blueprint, flash, redirect, render_template, request, json
from flask_login import login_required, current_user, logout_user

from languages import languages_ace
from models import Room, User, db, Invitations

flask_views = Blueprint("main_routes", "main_routes")

@flask_views.route("/create", methods=["GET", "POST"])
@login_required
def create_room():
    if not current_user.is_admin:
        flash("Please Login on an account that allows creating channels")
        return redirect('/login?next=/create')
    if request.form.get('room_name'):
        d = request.form.to_dict()
        d['active']=True
        d['owner_id'] = current_user.id
        d['invite_only'] = d['invite_only'] == "on"
        d['require_registered'] = d['require_registered'] == "on"
        Room.from_dict(d,commit=True)
        return redirect("/session/"+d['room_name'])
    ctx = dict(
        languages = sorted(languages_ace.items())
    )
    # themes = sorted(themes_ace.items())
    return render_template('create_session.html',**ctx)
@flask_views.route("/invite/<room_name>", methods=["GET", "POST"])
def invite(room_name):
    room = Room.query.filter_by(room_name=room_name).first()
    if not room:
        return "ERROR ROOM NOT FOUND!"
    if not current_user.is_admin and room.require_registered:
        return "Insufficient Authorization"
    if request.form:
        data = request.form.to_dict()
        user = User.get_or_create(**data)
        db.session.add(Invitations(user=user,room=room))
        db.session.commit()
        if data.get('as_json',False):
            return json.dumps({'user':user.to_dict()})

    # room = json.load(open(os.path.join(os.path.dirname(__file__), 'metadata', '%s.json' % room_name), "rb"))
    url = request.host_url.split("//",1)[0]+"//"+request.host+"/session/"+room.room_name
    return render_template('invite_candidate.html',room=room,url=url)


@flask_views.route("/session/<room_name>")
def view_session(room_name,username=''):
    room = Room.query.filter_by(room_name=room_name).first()
    if not room:
        return "Unable to find that room"

    if room.require_registered :
        if current_user.is_anonymous():
            return redirect("/login?next=/session/%s"%room_name)
        if not current_user.is_admin:
            if not current_user.is_active:
                return "Unauthorized"
            if room.invite_only:
                if current_user.id not in [invite.user.id for invite in room.invited_users] + [room.owner_id,]:
                    return "not authorized to enter room"
                if not room.active and current_user.id != room.owner_id:
                    return "Room no longer available"
        elif request.form:
            pass # if request.form.get('')
    try:
        username = current_user.username
    except:
        username = ""
    ctx = dict(
        room = room.to_dict(),
        username=username
    )
    return render_template('code_editor.html',**ctx)

@flask_views.route("/logout")
@login_required
def do_logout():
    logout_user()
    return redirect("/login")

@flask_views.route("/login",methods=["GET","POST"])
def do_login():
    if request.form:
        user = request.form.get('username',None)
        pw = request.form.get('password',None)
        if User.login(user,pw):
            return redirect(request.args.get("next","/"))
    return render_template("login.html")