import random
import string
import traceback

from flask import current_app, Flask, request
from flask_login import current_user
from flask_socketio import join_room, leave_room, SocketIO, disconnect, emit

from ..models import User, Room, db, Invitations
from .room_util import get_latest_prog, update_latest_prog

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('coderpad-socketio')
# logN = logging.getLogger('NOTIFY')
def emit2(event,*args,**kwargs):
    # if kwargs.get('broadcast',True) is False:
    #     logN.info("EMIT: %r => %s %s"%(event,args,kwargs))
    # else:
    #     logB.info("EMIT: %r => %s %s"%(event,args,kwargs))
    emit(event,*args,**kwargs)
class ActiveUsers:
    active_users_by_room={}
    active_users_by_sid={}
    active_sids_by_room = {}
    active_sids = set()
    pending_sids = set()
    @staticmethod
    def get_by_sid(sid):
        return ActiveUsers.active_users_by_sid[sid]


    @staticmethod
    def is_active(sid):
        return sid in ActiveUsers.active_sids
    @staticmethod
    def user_connected():
        ActiveUsers.pending_sids.add(request.sid)
    @staticmethod
    def get_room_users(room_name):
        return ActiveUsers.active_users_by_room.setdefault(room_name,[])

    @staticmethod
    def remove_user(sid):
        def remove_from_roomlist(room_name):
            room_list = ActiveUsers.active_users_by_room[room]
            idx = [u['sid'] for u in room_list].index(sid)
            del room_list[idx]
        ActiveUsers.active_sids.remove(sid)
        userData = ActiveUsers.active_users_by_sid.pop(sid)
        log.debug("Good bye: %s" % userData['username'])
        for room in userData['rooms']:
            log.debug("Leaving: %s" % room)
            ActiveUsers.active_sids_by_room[room].remove(sid)
            remove_from_roomlist(room)

        log.info("removed_user:", userData)
    @staticmethod
    def user_disconnected():
        if request.sid in ActiveUsers.pending_sids:
            ActiveUsers.pending_sids.remove(request.sid)
            log.info("User not authenticated yet, so nothing to do...")
            return
        if request.sid not in ActiveUsers.active_sids:
            raise Exception("User is not active")
        ActiveUsers.remove_user(request.sid)

    @staticmethod
    def add_to_room(room_name,userDataDict):
        my_sid = request.sid
        if my_sid not in ActiveUsers.pending_sids.union(ActiveUsers.active_sids):
            raise Exception("User does not appear to have connected!")
        if my_sid in ActiveUsers.pending_sids:
            ActiveUsers.pending_sids.remove(my_sid)

        my_rooms = userDataDict.setdefault('rooms', [])
        if room_name in my_rooms:
            raise Exception("Already in room!")
        my_rooms.append(room_name)
        userDataDict['sid'] = my_sid
        ActiveUsers.active_users_by_room.setdefault(room_name,[]).append(userDataDict)
        ActiveUsers.active_sids_by_room.setdefault(room_name,set()).add(request.sid)
        ActiveUsers.active_users_by_sid[request.sid] = userDataDict
        ActiveUsers.active_sids.add(request.sid)
        log.info("ADDED USER %s TO %s"%(userDataDict,room_name))
       # .add(room_name)
       #  Users.pending_sids.remove(my_sid)
       #  userDataDict['username']
    @staticmethod
    def is_authenticated(room_name):
        return request.sid in ActiveUsers.active_sids_by_room[room_name]
    @staticmethod
    def require_authentication(fn):
        def _inner_fn(*args,**kwargs):
            if not request.sid in ActiveUsers.active_sids:
                disconnect()
            return fn(*args,**kwargs)
        return _inner_fn
socketio = SocketIO()
@socketio.on('connect')
def on_connect():
    print( "OK CONNECTED:",request.sid )
    ActiveUsers.user_connected()
@socketio.on("disconnect")
def on_disconnect():
    ActiveUsers.user_disconnected()
@socketio.on('join')
def on_join(data):
    log.info("JOIN:",data,request.sid)
    try:
        user = User.query.filter_by(id=current_user.id)
    except:
        user = None

    username = data['username']
    room_name = data['room']
    room = Room.query.filter_by(room_name=room_name).first()
    if not room or not room.active:
        disconnect()
    if hasattr(current_user,'id') and current_user.id == room.owner_id:
        User.query.filter_by(id=current_user.id).update(dict(sid = request.sid))
        db.session.commit()
    if room.require_registered:
        if current_user.is_anonymous:
            disconnect()
        username = current_user.username
        try:
            user = User.query.filter_by(id=current_user.id).first()
        except:
            user = None
        if not user and current_user.is_admin is None:
            user = Invitations.get_my_invitation()
        user.sid=request.sid
        db.session.commit()
        if room.invite_only and not room.is_invited(current_user):
            print("User %s is not invited to room %s"%(current_user,room))
            disconnect()
    active_room_users = ActiveUsers.get_room_users(room.room_name)
    emit2('user_list', {'active_users':active_room_users,
                       'program_text':get_latest_prog(room.room_name)},broadcast=False)

    join_room(room.room_name)
    if current_user.is_anonymous:
        ActiveUsers.add_to_room(room_name,{'username':username,'id':random.choice(string.ascii_uppercase),"sid":request.sid,"is_AFK":False})

    else:
        ActiveUsers.add_to_room(room_name,current_user.to_dict())
    emit2('user_joined',{'username':username}, room=room_name)


@socketio.on('run')
@ActiveUsers.require_authentication
def on_run(data):
    emit2('user_run', {'username': data['username']}, room=data['room'])

@socketio.on('speak')
@ActiveUsers.require_authentication
def on_speech(data):
    data['message'] = data['message'].replace("\"","&quot;").replace("'","&#39;")
    emit('user_speech', data, room=data['room_details']['room'])

@socketio.on('leave')
def on_leave(data):
    print("GOODNIGHT?", data)
    if not data:return
    username = data['username']
    room_name = data['room']
    room = Room.query.filter_by(room_name=room_name).first()
    emit('user_left', {'username': username}, room=room_name)

@socketio.on("focus_lost")
def on_lost_focus(data):
    room_name = data['room_details']['room']
    room = Room.query.filter_by(room_name=room_name).first()
    if not room or not room.owner.sid:
        return
    user = User.query.filter_by(username=data['room_details']['username'], is_active='TRUE').first()
    if user:
        data['user_id'] = user.id
        user.is_AFK = True
        db.session.commit()
    data['action'] = "LOST"
    # print 'focus_update', data, room.owner.sid
    emit2('focus_update', data, room=room.owner.sid)
@socketio.on("focus_gained")
def on_focus_gained(data):
    room_name = data['room_details']['room']
    room = Room.query.filter_by(room_name=room_name).first()
    data['action']="GAINED"
    if room and room.owner.sid:
        user = User.query.filter_by(username=data['room_details']['username'],is_active='TRUE').first()
        if user:
            data['user_id'] = user.id
            user.is_AFK = False
            db.session.commit()
        emit2('focus_update', data, room=room.owner.sid)

@socketio.on('message')
def handle_message(message):
    print('received message.. not sure how or why: ' + message)

@socketio.on("sync_request")
@ActiveUsers.require_authentication
def request_sync(user_details):
    room_name = user_details['room_details']['room']
    if not ActiveUsers.is_authenticated(room_name):
        disconnect()
    room = Room.query.filter_by(room_name=room_name).first()
    if not room or not room.is_invited(current_user):
        disconnect()
    payload = {'program_text':get_latest_prog(room_name)}
    if hasattr(current_user,'is_admin') and current_user.is_admin:
        payload['active_users']=ActiveUsers.get_room_users(room_name)
        print("ACTIVE USERS:", payload['active_users'])
        active_ids = {u['id'] for u in payload['active_users']}
        payload['all_users']=[u.to_dict() for u in room.room_members()]
        for user in payload['all_users']:
            user['online'] = user['id'] in active_ids
    emit2('sync_result',payload)

def handle_change_message(data):
    room = data['room_details']['room']
    current_text_lines = get_latest_prog(room).splitlines()
    start_line = data['start']['row']
    end_line = data['end']['row']
    try:
        end_line_text = current_text_lines[end_line]
    except IndexError:
        end_line_text = ""
    try:
        start_line_text = current_text_lines[start_line]
    except:
        start_line_text=""
    if (data['action'] == "insert"):
        print("INSERT?",data)
        line0 = data['lines'].pop(0)
        lhs = start_line_text[0:data['start']['column']]
        rhs = start_line_text[data['start']['column']:]
        if (not data['lines']):
            try:
                current_text_lines[start_line] = lhs + line0 + rhs
            except IndexError:
                current_text_lines.append(lhs + line0 + rhs)
        else:
            current_text_lines[start_line] = lhs + line0;
            lineN = data['lines'].pop()
            data['lines'].append(lineN+rhs)
            current_text_lines[start_line + 1:start_line + 1] = data['lines']



    elif (data['action'] == "remove"):
        try:
            lhs = start_line_text[0:data['start']['column']]
        except:
            lhs = ""
        try:
            rhs = end_line_text[data['end']['column']:]
        except IndexError:
            rhs = ""
        new_line = lhs + rhs
        current_text_lines[start_line:end_line+1] = [new_line,]
    update_latest_prog(room,"\n".join(current_text_lines))

@socketio.on('on_editor_change')
@ActiveUsers.require_authentication
def handle_editor_change(message):
    socketio = current_app.extensions['socketio']
    room = message['room_details']['room']
    if not ActiveUsers.is_authenticated(room):
        disconnect()
    emit2('editor_change_event',message, room=room)
    handle_change_message(message)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("host",nargs="?")
    parser.add_argument("port",nargs="?")
    parser.add_argument("-p","--portnum",default="5678")
    args = parser.parse_args()
    if not args.host:
        args.host = "127.0.0.1"
    args.port = args.port or args.portnum
    print("Serving Sockets @ ws://%s:%s"%(args.host,args.port))
    app = Flask(__name__)
    socketio.init_app(app)
    socketio.run(app,args.host,args.port)