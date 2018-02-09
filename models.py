import base64
import hashlib
import json
import random

import re

import os

import datetime
from flask import request, session
from flask_login import LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy

from room_util import get_progam_stat

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
    def create_guest(cls,email):
        username=email.split("@",1)[0]
        return User(id=random.randint(1000000,100000000),email=email,username=username,realname=re.sub("([a-z])([A-Z])","\\1 \\2",username.title()))
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


    @property
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
        try:
            pw = hashlib.md5(password).hexdigest()
        except TypeError:
            pw = hashlib.md5(password.encode("latin1")).hexdigest()
        print("PW:", pw)
        user = User.query.filter_by(username=username,
                                    password=pw,
                                    ).first()
        if user:
            login_user(user)
        return user

    @staticmethod
    @login_manager.user_loader
    def user_loader(token):
        try:
            user = User.query.filter_by(email=token).first()
        except:
            pass
        if not user and session.get("X-token-coderpad",None):
            invite_token = base64.b64decode(session['X-token-coderpad']).decode('latin1')
            invitation = Invitations.query.filter_by(invite_code=invite_token).first()
            if invitation.room.active:
                return User.create_guest(invitation.email_address)
        return user




class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String(120))
    email_address = db.Column(db.String(120))
    sid = db.Column(db.String(120),nullable=True,default=None)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'),
                        nullable=False)
    room = db.relationship('Room',
                           backref=db.backref('invited_users', lazy=True))
    @staticmethod
    def get_my_invitation():
        tokb64 = session.get("X-token-coderpad", None)
        if not tokb64:
            return None
        return Invitations.query.filter_by(invite_code=base64.b64decode(tokb64)).first()
    def to_dict(self):
        return {'id':self.id,'email_address':self.email_address,'invite_code':self.invite_code,'room':self.room.to_dict()}

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
        return [self.owner,] + [User.create_guest(i.email_address) for i in self.invited_users]
    def created(self):
        st = get_progam_stat(self.room_name)
        return datetime.datetime.fromtimestamp(st.st_ctime)
    def last_modified(self):
        st = get_progam_stat(self.room_name)
        return datetime.datetime.fromtimestamp(st.st_mtime)

    def is_invited(self,user):
        if not self.require_registered:
            return True
        if not self.invite_only:
            return not user.is_anonymous()

        return user.email in [u.email for u in self.room_members()]
    def to_dict(self):
        return {
            'id':self.id,
            'owner_id':self.owner_id,
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