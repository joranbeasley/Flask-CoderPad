import hashlib

from flask_login import LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    sid = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    realname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    is_AFK = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    @classmethod
    def get_or_create(cls,username,password,realname,email,**kwargs):
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User()
            db.session.add(user)
        user.username = username
        user.password = password
        user.email = email
        user.realname = realname
        for k in kwargs:
            if isinstance(getattr(user,k,None),db.Column):
                setattr(user,k,kwargs[k])
        return user

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'is_admin': self.is_admin,
                'is_active': self.is_active, 'username': self.username,
                'realname': self.realname, 'is_AFK':self.is_AFK}

    def is_authenticated(self):
        return True



    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)

    def __repr__(self):
        return '<User %r>' % self.username

    def display_name(self):
        try:
            return self.realname.split()[0] or self.username
        except IndexError:
            return self.username

    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username,
                                    password=hashlib.md5(password).hexdigest()
                                    ).first()
        if user:
            login_user(user)
        return user

    @staticmethod
    @login_manager.user_loader
    def user_loader(token):
        return User.query.filter_by(email=token).first()



class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('rooms', lazy=True))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'),
                        nullable=False)
    room = db.relationship('Room',
                           backref=db.backref('invited_users', lazy=True))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(120), unique=True, nullable=False)
    room_language = db.Column(db.String(120), nullable=False, default="python")
    active = db.Column(db.Boolean, default=True)
    require_registered = db.Column(db.Boolean, default=True)
    invite_only = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                         nullable=False)
    owner = db.relationship('User',
                            backref=db.backref('owned_rooms', lazy=True))
    def room_members(self):
        return [self.owner,] + [i.user for i in self.invited_users]
    def is_invited(self,user):
        if not self.require_registered:
            return True
        if not self.invite_only:
            return not user.is_anonymous()

        return user.id in [u.id for u in self.room_members()]
    def to_dict(self):
        return {'owner_id':self.owner_id,
            'room_name':self.room_name,
            'require_registered':self.require_registered,
            'invite_only':self.invite_only,
            'active':self.active,
            'members':[member.to_dict() for member in self.room_members()],
        }
    @classmethod
    def from_dict(cls,data,commit=False):
        new_data = {key:value for key,value in data.items() if hasattr(cls,key)}
        room = Room(**new_data)
        db.session.add(room)
        if commit:
            db.session.commit()
        return room