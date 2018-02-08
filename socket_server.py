import traceback

from flask import current_app, Flask, request
from flask_login import current_user
from flask_socketio import join_room, leave_room, SocketIO, disconnect, emit

from models import User, Room, db, Invitations
from room_util import get_latest_prog, update_latest_prog


active_users = {}
socketio = SocketIO()
@socketio.on('join')
def on_join(data):
    try:
        user = User.query.filter_by(id=current_user.id)
    except:
        user = None

    username = data['username']
    room_name = data['room']
    room = Room.query.filter_by(room_name=room_name).first()
    if not room or not room.active:
        disconnect()

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
            print "User %s is not invited to room %s"%(current_user,room)
            disconnect()

    emit('user_list', {'active_users':active_users.setdefault(room.room_name,[]),
                       'program_text':get_latest_prog(room.room_name)},broadcast=False)
    # emit('sync',{'program_text':get_latest_prog(room)},room=room,broadcast=False)
    print "EMIT:psynch",{'program_text':get_latest_prog(room.room_name)}
    join_room(room.room_name)
    if current_user.is_anonymous:
        active_users[room.room_name].append({'username':username})
    else:
        active_users[room.room_name].append(current_user.to_dict())
    emit('user_joined',{'username':username}, room=room)
@socketio.on('run')
def on_run(data):
    emit('user_run', {'username': data['username']}, room=data['room'])

@socketio.on('speak')
def on_speech(data):
    data['message'] = data['message'].replace("\"","&quot;").replace("'","&#39;")
    print "SAY:",data
    emit('user_speech', data, room=data['room_details']['room'])

@socketio.on('leave')
def on_leave(data):
    if not data:return
    username = data['username']
    room_name = data['room']
    room = Room.query.filter_by(room_name=room_name).first()
    if not room:
        print "NO ROOM ADIOS!!"
        disconnect()
        return
    if room.require_registered:
        if current_user.is_anonymous:
            print "NO ANON!!! ADIOS!!"
            disconnect()
            return
        try:
            idx = [u['username'] for u in active_users[room.room_name]].index(current_user.username)
        except:
            traceback.print_exc()
            print "NO IDX!!!"
            disconnect()
            return
        else:
            username = current_user.username
            try:
                user = User.query.filter_by(id=current_user.id).first()
            except:
                user = None
            if not user:
                user = Invitations.get_my_invitation()
            user.sid=None
            db.session.commit()
            ex_user = active_users[room.room_name].pop(idx)
            print "POPPED:",ex_user,"@",idx
    leave_room(room_name)
    emit('user_left', {'username': username}, room=room)

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
    print 'focus_update', data, room.owner.sid
    emit('focus_update', data, room=room.owner.sid)
@socketio.on("focus_gained")
def on_focus_gained(data):
    print(data)
    room_name = data['room_details']['room']
    room = Room.query.filter_by(room_name=room_name).first()
    data['action']="GAINED"
    if room and room.owner.sid:
        user = User.query.filter_by(username=data['room_details']['username'],is_active='TRUE').first()
        if user:
            data['user_id'] = user.id
            user.is_AFK = False
            db.session.commit()
        emit('focus_update', data, room=room.owner.sid)

@socketio.on('message')
def handle_message(message):
    print('received message.. not sure how or why: ' + message)

@socketio.on("sync_request")
def request_sync(user_details):
    room_name = user_details['room_details']['room']
    room = Room.query.filter_by(room_name=room_name).first()
    if not room or not room.is_invited(current_user):
        disconnect()
    payload = {'program_text':get_latest_prog(room_name)}
    if current_user.is_admin:
        payload['active_users']=active_users[room_name]
        active_ids = {u['id'] for u in payload['active_users']}
        payload['all_users']=[u.to_dict() for u in room.room_members()]
        for user in payload['all_users']:
            user['online'] = user['id'] in active_ids
    emit('sync_result',payload)

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
def handle_editor_change(message):
    socketio = current_app.extensions['socketio']
    room = message['room_details']['room']
    emit('editor_change_event',message, room=room)
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