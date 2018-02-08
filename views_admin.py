import json

from flask import Blueprint, flash, redirect, request, render_template
from flask_login import login_required, current_user

from languages import languages_ace
from models import Room, User, db, Invitations
from room_util import update_latest_prog
from socket_server import active_users

admin_views = Blueprint("admin_routes", "admin_routes")

@admin_views.route("/create_room", methods=["GET", "POST"])
@login_required
def create_room():
    if not current_user.is_admin:
        flash("Please Login on an account that allows creating channels")
        return redirect('/admin/login?next=/create')
    if request.form.get('room_name'):
        d = request.form.to_dict()
        d['active']=True
        d['owner_id'] = current_user.id
        d['invite_only'] = d.get('invite_only',False) == "on"
        d['require_registered'] = d.get('require_registered',False) == "on"
        update_latest_prog(d['room_name'],'')
        Room.from_dict(d,commit=True)
        return redirect("/session/"+d['room_name'])
    ctx = dict(
        languages = sorted(languages_ace.items())
    )
    return render_template('create_session.html',**ctx)


@admin_views.route("/invite/<room_name>", methods=["GET", "POST"])
@login_required
def invite(room_name):
    room = Room.query.filter_by(room_name=room_name).first()
    if not room:
        return "ERROR ROOM NOT FOUND!"
    if not current_user.is_admin and room.require_registered:
        return "Insufficient Authorization"
    if request.form:
        data = request.form.to_dict()
        user = User.get_or_create(**data)
        db.session.add(Invitations(user=user, room=room))
        db.session.commit()
        if data.get('as_json', False):
            return json.dumps({'user': user.to_dict()})

    # room = json.load(open(os.path.join(os.path.dirname(__file__), 'metadata', '%s.json' % room_name), "rb"))
    url = request.host_url.split("//", 1)[0] + "//" + request.host + "/session/" + room.room_name
    return render_template('invite_candidate.html', room=room, url=url)

# @admin_views.route("/room_activation/<room_id>/<enabled>")
# @login_required
# def list_rooms(room_id,enabled):
#     Room.query.filter_by(id=room_id).update(active=bool(int(enabled)))
#     db.session.commit()

@admin_views.route("/list_rooms")
@login_required
def list_rooms():
    if not current_user.is_admin:
        return redirect("/login?next=/admin/list_rooms")
    rooms = Room.query.all()
    total_active_users = [len(room_ppl) for room_ppl in active_users.values()]
    return render_template("rooms_list.html",rooms=rooms,active_users=active_users,ttl_active_users=total_active_users)
