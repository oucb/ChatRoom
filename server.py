# -*- coding: utf-8 -*-
# !/usr/bin/python
# file: server.py


import socket
import asyncore
from asynchat import async_chat
from asyncore import dispatcher

port = 3333
magic = 'oucb'
# magic is the Pass Phrase, 'oucb' for default, set by yourself


class EndSession(Exception):
    pass


class CommandHandler(object):
    def unknow(self, session, cmd):
        session.push('Unknow command: %s\n' % cmd)

    def handle(self, session, line):
        if not line.strip():
            return
        rec = line.split(' ', 1)
        cmd = rec[0]
        try:
            line = rec[1].strip()
        except IndexError:
            line = ''
        meth = getattr(self, 'do_' + cmd, None)
        try:
            meth(session, line)
        except TypeError:
            self.unknow(session, cmd)


class ChatSession(async_chat):
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator('\n')
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
            # enter中定义了self.room属性,因此调用handle方法时,getattr方法查找相应的self.room中的方法属性
            # 从客户端发送过来的命令处理后要能在相应的self.room实例中找到对于的方法属性,或是在父类Room中存在
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))
        # 在chatRoom时,查找do_logout方法属性,由于是在父类存在,所以可以调用


class Room(CommandHandler):
    def __init__(self, server):
        self.server = server
        self.session = []

    def add(self, session):
        self.session.append(session)

    def remove(self, session):
        self.session.remove(session)

    def broadcast(self, line):
        for session in self.session:
            session.push(line)

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):

    def add(self, session):
        Room.add(self, session)
        # 为了从loginRoom进入chatRoom时执行的self.room.remove不会报错,若不调用add方法,session属性为空列表,执行remove会报错
        session.push('Connect Success')

    def do_login(self, session, line):
        rec = line.split('+', 1)
        magic = rec[0]
        try:
            name = rec[1]
        except IndexError:
            name = ''
        if not magic:
            session.push('Passphrase Empty')
        elif magic != self.server.magic:
            session.push('Passphrase Incorrect')
        else:
            if not name:
                session.push('User name Empty')
            elif name in self.server.users:
                session.push('User name Exit')
            else:
                session.name = name
                session.enter(self.server.main_room)
            # 这里保证了进入共用的chatRoom实例,而后后调用相关的方法,能使用全局同步的session与server属性,如果换成chatRoom(self.server),
            # 则相当于每次调用enter都对chatRoom进行实例化,并进入各自相应的实例,session属性都将重置为空列表


class ChatRoom(Room):

    def add(self, session):
        session.push('Login Success!')
        self.broadcast(session.name + ' has enter the room.\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        Room.remove(self, session)
        self.broadcast(session.name + ' has left the room.\n')

    def do_say(self, session, line):
        self.broadcast(session.name + ': ' + line + '\n')

    def do_look(self, session, line):
        session.push('Online users:\n')
        for other in self.session:
            session.push(other.name + '\n')


class LogoutRoom(Room):

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatServer(dispatcher):
    def __init__(self, port, magic):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)
        self.magic = magic
        # 预先实例化chatRoom,由于没有__init__()方法,因此执行父类Room的初始化方法,拥有server与session属性,供后面每个会话从loginRoom
        # 进入chatRoom时引用,从而为每个会话提供全局同步的server与session属性,这样每个新加入chatRoom的用户可查询到其它的用户

    def handle_accept(self):
        con, addr = self.accept()
        ChatSession(self, con)

if __name__ == '__main__':
    s = ChatServer(port, magic)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print
