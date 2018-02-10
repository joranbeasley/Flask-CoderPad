import json

from flask import Blueprint, flash, redirect, request, render_template
from flask_login import login_required, current_user

from ..languages import languages_ace
from ..models import Room, User, db, Invitations
from ..coderpad_socket_server.room_util import update_latest_prog
from ..coderpad_socket_server.socket_server import ActiveUsers

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
    return render_template('create_session.html', **ctx)


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

@admin_views.route("/")
@login_required
def admin_index():
    if not current_user.is_admin:
        return redirect("/login?next=/admin/list_rooms")
    rooms = Room.query.all()
    total_active_users = [len(room_ppl) for room_ppl in ActiveUsers.active_users_by_room.values()]
    ctx = dict(
        rooms=rooms, active_users=ActiveUsers.active_users_by_room, ttl_active_users=total_active_users,
        users = User.query.all()
    )
    return render_template("admin_index.html", **ctx)


@admin_views.route("/add_new_admin_user",methods=["GET","POST"])
@login_required
def new_admin_user():
    if not current_user.is_admin:
        return redirect("/login?next=/admin/add_new_admin_user")
    if request.form:
        data = request.form.to_dict()

        user = User.get_or_create(**data)
        user.is_admin = True
        # db.session.add(Invitations(user=user, room=room))
        db.session.commit()
        flash("USER ADDED")
        return redirect("/")
    return render_template('invite_candidate.html')

@admin_views.route("/delete/<what>/<item_pk>")
@login_required
def delete_item(what,item_pk):
    item = None
    if what == "user":
        item = User.query.get(item_pk)
    elif what == "room":
        item = Room.query.get(item_pk)
    if not item:
        return {"error":"Unknown Item %r=>%r"%(what,pk)}
    # item.delete()
    db.session.delete(item)
    db.session.commit()

    if request.args.get('as_json',False):
        return json.dumps({"deleted_%s"%what:item.to_dict()})
    return redirect("/admin")