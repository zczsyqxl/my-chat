import wx
import threading
import socket
from time import sleep, ctime 
from enum import Enum, IntEnum, unique
import os
import sys
import signal
import getpass

class StyleList(Enum):
    OUTPUT = 2
    SEND = 3
    RECE = 4

class MyStyle(wx.TextAttr):
    def __init__(self, style = None):
        wx.TextAttr.__init__(self)
        self.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        self.SetFontSize(12)
        self.__SetSty(style)
    def __SetSty(self, style):
        if StyleList.OUTPUT == style:
            self.SetTextColour(wx.RED)
        elif StyleList.SEND == style:           
            self.SetTextColour(wx.Colour(30,25,125))
            self.SetAlignment(wx.TEXT_ALIGNMENT_RIGHT)
            self.SetParagraphSpacingBefore(20)
        elif StyleList.RECE == style:
            self.SetTextColour(wx.BLUE)
            self.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            self.SetParagraphSpacingBefore(20)
        else:
            pass

class Data():     
    __remoteIp = ''   
    @classmethod
    def GetLocalIp(cls):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    @classmethod
    def GetHostName(cls):
        hostName = socket.gethostname()
        return hostName
    @classmethod
    def GetUser(cls):
        user = getpass.getuser()
        return user
    @classmethod
    def GetServerPort(cls):
        return 12345
    @classmethod
    def GetClientPort(cls):
        return 54321
    @classmethod
    def SetRemoteIp(cls,remoteIp):
        Data.__remoteIp = remoteIp
    @classmethod
    def GetRemoteIp(cls):
        return Data.__remoteIp

class MyServer(socket.socket):
    def __init__(self):
        socket.socket.__init__(self,socket.AF_INET,socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((Data.GetLocalIp(),Data.GetServerPort()))
        self.listen(1)
    def CreateMyServer(self):
        try:
            self.conn, self.add = self.accept()
        except Exception as e:
            self.close()
            if ChatWindow.tclock.acquire():
                #newWin.outMsg.Clear()
                #newWin.outMsg.AppendText(str(e)+'1\n')
                ChatWindow.tclock.release()
        else:            
            newWin.Connected(False,self.add[0])            
            self.SeReceive()
            
    def SeReceive(self):
        while True:
            try:
                info = self.conn.recv(1024).decode()           
            except Exception as e:
                self.close()
                if ChatWindow.tclock.acquire():
                    newWin.outMsg.Clear()
                    newWin.outMsg.AppendText(str(e)+'\n')
                    ChatWindow.tclock.release()
                    newWin.StartServer()
                break              
            else:
                if ChatWindow.tclock.acquire(): 
                    ll = newWin.outMsg.GetLastPosition()
                    newWin.outMsg.AppendText(info+'\n')
                    l = newWin.outMsg.GetLastPosition()
                    newWin.outMsg.SetStyle(ll,l,MyStyle(StyleList.RECE))
                ChatWindow.tclock.release() 

    
class MyClient(socket.socket):
    def __init__(self):
        socket.socket.__init__(self,socket.AF_INET,socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((Data.GetLocalIp(),Data.GetClientPort()))
        return
    def CreatMyClient(self):
        try:
            self.connect((Data.GetRemoteIp(),Data.GetServerPort()))
        except Exception as e:
            self.close()
            if ChatWindow.tclock.acquire():
                newWin.outMsg.Clear()
                newWin.outMsg.AppendText(str(e)+'\n')
                ChatWindow.tclock.release()
                newWin.StartServer()
        else:
            newWin.Connected(True,Data.GetRemoteIp())
            self.Receive()
                        
    def Receive(self):
        while True:
            try:
                info = self.recv(1024).decode()
            except Exception as e:
                self.close()
                if ChatWindow.tclock.acquire():
                    newWin.outMsg.Clear()
                    newWin.outMsg.AppendText(str(e)+'\n')
                    ChatWindow.tclock.release()
                    newWin.StartServer()
                break
            else:
                if ChatWindow.tclock.acquire():    
                    ll = newWin.outMsg.GetLastPosition()
                    newWin.outMsg.AppendText(info+'\n')
                    l = newWin.outMsg.GetLastPosition()
                    newWin.outMsg.SetStyle(ll,l,MyStyle(StyleList.RECE))  
                ChatWindow.tclock.release()       
         
class ChatWindow(wx.Frame):    
    tclock = threading.Lock()
    flag = False
    def __init__(self, parent, title):
        super().__init__(parent,title=title,size=(400,600))
        self.InitUI()
        self.Center()
        self.Show()
        self.StartServer()
    def InitUI(self):
        self.panel = wx.Panel(self) 
        self.hostAddress = wx.TextCtrl(self.panel, style = wx.TE_RICH|wx.TE_RICH2)       
        self.inputMsg = wx.TextCtrl(self.panel, style = wx.TE_RICH|wx.TE_RICH2|wx.TE_PROCESS_ENTER)        
        self.inputMsg.Bind(wx.EVT_TEXT_ENTER,self.SentEvent)        
        self.connectButton = wx.Button(self.panel,label = '连接')
        self.connectButton.Bind(wx.EVT_BUTTON,self.ClickConnectButton)
        self.outMsg = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.TE_RICH2)
               
        self.hBox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hBox2 = wx.BoxSizer(wx.HORIZONTAL)    
        self.vBox = wx.BoxSizer(wx.VERTICAL)
        
        self.hBox1.Add(self.hostAddress, proportion = 10, flag = wx.EXPAND|wx.ALL, border = 3)
        self.hBox1.Add(self.connectButton, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 3)
        self.hBox2.Add(self.inputMsg, proportion = 10, flag = wx.EXPAND|wx.ALL, border = 3)
        
        self.vBox.Add(self.hBox1, proportion = 1, flag = wx.EXPAND|wx.ALL,border = 3)
        self.vBox.Add(self.outMsg, proportion = 10, flag = wx.EXPAND|wx.ALL,border = 6)
        self.vBox.Add(self.hBox2, proportion = 1, flag = wx.EXPAND|wx.ALL,border = 3)
        
        self.panel.SetSizer(self.vBox) # 设置主尺寸器 
       
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
    def OnCloseWindow(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to quit?','Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_YES:
            self.server.close()
            try:
                self.client.close()
            except:                
                pass            
            self.Destroy()
        else:
            event.Veto()    
    
    def ClickConnectButton(self, event):
        
        if ChatWindow.flag == False:
            self.server.close()   
            self.client = MyClient()
            Data.SetRemoteIp(self.hostAddress.GetValue())      
            self.hostAddress.Clear()
            self.hostAddress.Enable(False)
            self.connectButton.Enable(False)  
            self.outMsg.Clear()
            self.outMsg.AppendText("连接中………………\n")
            self.ctd = threading.Thread(target = self.client.CreatMyClient)
            self.ctd.start()
        elif ChatWindow.flag == True:
            try:
                self.server.conn.close()
            except:
                pass
            finally:
                try:
                    self.server.close()
                except:
                    pass           
            try:
                self.client.close()
            except:
                pass
            self.outMsg.AppendText("已断开\n")         
                
    def SentEvent(self, event):    
        if self.std.isAlive():
            try:
                self.server.conn.send(self.inputMsg.GetValue().encode())
            except Exception as e:
                if ChatWindow.tclock.acquire():
                    newWin.outMsg.Clear()
                    newWin.outMsg.AppendText(str(e)+'\n')
                    ChatWindow.tclock.release()              
        elif self.ctd.isAlive():
            try:
                self.client.send(self.inputMsg.GetValue().encode())
            except Exception as e:
                if ChatWindow.tclock.acquire():
                    newWin.outMsg.Clear()
                    newWin.outMsg.AppendText(str(e)+'\n')
                    ChatWindow.tclock.release()
        if ChatWindow.tclock.acquire():    
            ll = self.outMsg.GetLastPosition()
            self.outMsg.AppendText(self.inputMsg.GetValue() +'\n')
            l = self.outMsg.GetLastPosition()
            self.outMsg.SetStyle(ll,l,MyStyle(StyleList.SEND))
            self.inputMsg.Clear()
            self.inputMsg.SetDefaultStyle(MyStyle())
            ChatWindow.tclock.release()
        
    def StartServer(self):       
        ChatWindow.flag = False
        self.hostAddress.Enable(True)
        self.hostAddress.SetDefaultStyle(MyStyle())
        self.connectButton.Enable(True)  
        self.connectButton.SetLabel("连接") 
        self.inputMsg.Enable(False)
        self.inputMsg.SetDefaultStyle(MyStyle())
        
        self.outMsg.SetDefaultStyle(MyStyle(StyleList.OUTPUT))
        self.outMsg.AppendText('==========================\n')
        self.outMsg.AppendText('请输入对方IP进行连接\n')
        self.outMsg.AppendText('******或者****************\n')
        self.outMsg.AppendText('等待对方与你进行连接\n')
        self.outMsg.AppendText('--------------------------\n')
        self.outMsg.AppendText('你的IP为:【' + Data.GetLocalIp() + '】\n')
        self.outMsg.AppendText('==========================\n')
        
        self.server = MyServer() 
        self.std = threading.Thread(target = self.server.CreateMyServer)
        self.std.start()
        
    def Connected(self,mode,ip = '0.0.0.0'):
        ChatWindow.flag = True
        self.inputMsg.Enable(True)
        self.hostAddress.Clear()       
        self.hostAddress.Enable(False)
        self.connectButton.Enable(True) 
        self.connectButton.SetLabel("断开") 
        self.outMsg.Clear()
        self.outMsg.AppendText("==================================\n")
        if mode == True:
            self.outMsg.AppendText("【你】已与【" + ip + "】连接成功\n")
        else:
            self.outMsg.AppendText("【" + ip + "】"+ "已与【你】连接成功\n")
        self.outMsg.AppendText("**********************************\n")
        self.outMsg.AppendText("【你们】可以愉快的进行聊天了\n")
        self.outMsg.AppendText("==================================\n")
                       
if __name__ == "__main__":
    app = wx.App()
    newWin = ChatWindow(None, title='Test')
    app.MainLoop()
