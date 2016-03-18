# -*- coding: utf-8 -*-
# !/usr/bin/python
# client.py

import wx
import telnetlib
import thread
from time import sleep


class Client(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.loginUI()
        self.Centre()
        self.Show()

    def loginUI(self):

        panel = wx.Panel(self)
        panel.SetBackgroundColour('#E1E3D6')

        # self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        self.font = wx.Font(19, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.font.SetPointSize(19)

        box = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        address_name = wx.StaticText(panel, label='Server Address:')
        address_name.SetFont(self.font)
        self.address = wx.TextCtrl(panel)
        self.address.SetBackgroundColour('#D8FFE7')
        box1.Add(address_name, flag=wx.UP, border=31)
        box1.Add(self.address, proportion=1, flag=wx.EXPAND | wx.UP | wx.RIGHT, border = 31)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        magic_name = wx.StaticText(panel, label='    Pass Phrase:')
        magic_name.SetFont(self.font)
        self.magic = wx.TextCtrl(panel)
        self.magic.SetBackgroundColour('#D8FFE7')
        bmagic = wx.BoxSizer(wx.HORIZONTAL)
        bmagic.Add(self.magic, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=31)
        box2.Add(magic_name, flag=wx.UP, border=17)
        box2.Add(bmagic, proportion=1, flag=wx.EXPAND | wx.UP | wx.BOTTOM, border=15)

        box3 = wx.BoxSizer(wx.HORIZONTAL)
        User_name = wx.StaticText(panel, label='      User Name:')
        User_name.SetFont(self.font)
        self.name = wx.TextCtrl(panel)
        self.name.SetBackgroundColour('#D8FFE7')
        box3.Add(User_name, flag=wx.UP, border=1)
        box3.Add(self.name, proportion=1, flag=wx.EXPAND | wx.BOTTOM | wx.RIGHT, border=31)

        box4 = wx.BoxSizer()
        login = wx.Button(panel, label='Login')
        login.Bind(wx.EVT_BUTTON, self.login)
        box4.Add(login)

        box.Add(box1, proportion=1, flag=wx.EXPAND | wx.UP, border=7)
        box.Add(box2, proportion=1, flag=wx.EXPAND | wx.UP, border=7)
        box.Add(box3, proportion=1, flag=wx.EXPAND | wx.UP, border=7)
        box.Add(box4, flag=wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, border=11)
        panel.SetSizer(box)

    def login(self, evt):
        try:
            serveraddress = self.address.GetLineText(0).split(':')
            con.open(serveraddress[0], port=int(serveraddress[1]), timeout=10)
            response = con.read_some()
            if response != 'Connect Success':
                self.showDialog('Error', 'Connect Fail!', (223, 111))
                return
            con.write('login ' + str(self.magic.GetValue()) + '+' + str(self.name.GetValue()) + '\n')
            # magic和name中间应加入识别符,以防止magic为空时,把输入的name挂钩到magic上,这里使用'+'
            # con.write('login ' + str(self.name.GetValue()) + '\n')
            response = con.read_some()
            if response == 'Passphrase Empty':
                self.showDialog('Error', 'Passphrase Empty!', (223, 111))
            elif response == 'Passphrase Incorrect':
                self.showDialog('Error', 'Passphrase Incorrect!', (223, 111))
            elif response == 'User name Empty':
                self.showDialog('Error', 'User name Empty!', (223, 111))
            elif response == 'User name Exit':
                self.showDialog('Error', 'User name Exit!', (223, 111))
            else:
                self.Close()
                Chat(None, title='Chat Room: ' + str(self.name.GetValue()))
        except Exception:
            self.showDialog('Error', 'Connect fail!', (223, 111))

    def showDialog(self, title, content, size):
        dialog = wx.Dialog(self, title=title, size=size, name=content)
        dialog.SetBackgroundColour('#E1E3D6')
        dialog.Center()

        panel = wx.Panel(dialog)
        box = wx.BoxSizer(wx.VERTICAL)
        bt = wx.Button(panel, wx.ID_OK, "OK")
        dlg = wx.StaticText(panel, id=wx.ID_ANY, label=content, pos=(61, 19))
        dlg.SetFont(self.font)
        dlg.SetForegroundColour('#E41F36')
        # box1 = wx.BoxSizer()
        # box1.Add(dlg, proportion=1, flag=wx.ALIGN_CENTER)
        box.Add(dlg, proportion=1, flag=wx.ALIGN_CENTER | wx.UP, border=19)
        box.Add(bt, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)
        panel.SetSizer(box)

        dialog.ShowModal()
        dialog.Destroy()


class Chat(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Chat, self).__init__(*args, **kwargs)
        self.chatUI()
        self.Centre()
        thread.start_new_thread(self.receive, ())
        self.Show()

    def chatUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#E1E3D6')

        box = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.BoxSizer()
        self.chatshow = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.HSCROLL)
        self.chatshow.SetBackgroundColour('#FEF1B5')
        box1.Add(self.chatshow, proportion=1, flag=wx.EXPAND)

        box2 = wx.BoxSizer()
        self.message = wx.TextCtrl(panel)
        self.message.SetBackgroundColour('#D8FFE7')
        bt_send = wx.Button(panel, label='send', size=(47, 30))
        bt_users = wx.Button(panel, label='users', size=(47, 30))
        bt_close = wx.Button(panel, label='close', size=(47, 30))
        bt_send.Bind(wx.EVT_BUTTON, self.send)
        bt_users.Bind(wx.EVT_BUTTON, self.lookusers)
        bt_close.Bind(wx.EVT_BUTTON, self.close)
        box2.Add(self.message, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        # box2默认为水平方向,proportion=1,即水平方向空间所占比例为1,而box2中其它控件的比例默认为0,
        # 因此box2伸缩时水平空间变化全作用于self.message,故此处可省略wx.EXPAND
        box2.Add(bt_send, flag=wx.RIGHT, border=1)
        box2.Add(bt_users, flag=wx.RIGHT, border=1)
        box2.Add(bt_close, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=5)

        box.Add(box1, proportion=1, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        box.Add(box2, proportion=0, flag=wx.EXPAND | wx.BOTTOM, border=5)
        # box为垂直方向,proportion=0,即box2垂直方向空间所占比例为0,所以伸缩变化时box2垂直方向不变,只做水平方向伸缩
        panel.SetSizer(box)

    def send(self, evt):
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            con.write('say ' + message + '\n')
            self.message.Clear()

    def lookusers(self, evt):
        con.write('look\n')

    def close(self, evt):
        con.write('logout\n')
        con.close()
        self.Close()

    def receive(self):
        while True:
            sleep(0.6)
            result = con.read_very_eager()
            if result != '':
                self.chatshow.AppendText(result)


if __name__ == '__main__':
    app = wx.App()
    con = telnetlib.Telnet()
    Client(None, title='Client Login')
    app.MainLoop()
