import socket
import re
from enum import Enum

class machineStatus(Enum):
    Ready = 0
    Busy = 1
    Building = 2
    Transfer = 3

class Controller(object):
    """Adventurer3との通信用制御クラス"""

    Adventurer3Port = 8899  # Adventurer3への接続ポート番号(一応固定)

    def __init__(self, hostname):
        """コンストラクタ"""
        self.hostname = hostname

    def Start(self):
        """Adventurer3との接続開始"""
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except OSError:
            return False
        self.tcp.connect((self.hostname, self.Adventurer3Port))
        self.tcp.send("~M601 S1\r\n".encode())
        self.Recv()
        return True

    def End(self):
        """Adventurer3との接続解除"""
        if self.IsConnected:
            self.tcp.send("~M602 S1\r\n".encode())
            self.Recv()
            self.tcp.close()
            self.tcp = None

    def Recv(self):
        '''データの受信'''
        data = self.tcp.recv(4096)
        if not data:
            return None
        else:
            return data.decode('utf-8')

    def Send(self, data):
        """データの送信"""
        if self.IsConnected:
            sendData = "~" + data
            try:
                self.tcp.send(sendData.encode())
                return self.Recv()
            except OSError:
                return ""

    def IsConnected(self):
        """Adventurer3と接続中かどうか"""
        if not self.tcp:
            return False
        else:
            return True

    def IsOk(self, data):
        """返ってきたデータがOKかどうかの判断"""
        if not data:
            return False
        else:
            trimLine = data.strip()
            if trimLine.endswith("ok") >= 0:
                return True
            elif trimLine.endswith("ok.") >= 0:
                return True
            else:
                return False

    def UpdateMachneStatus(self):
        """機器の状態取得"""
        work = self.Send("M119")
        if self.IsOk(work):
            split = work.split("\n")
            for line in split:
                trimLine = line.strip()
                if trimLine.startswith("Endstop"):
                    endstop = trimLine.split(' ')
                    if len(endstop) == 4:
                        self.LimitX = self.LimitY = self.LimitZ = True
                        if endstop[1].endswith("0"):
                            self.LimitX = False
                        if endstop[2].endswith("0"):
                            self.LimitY = False
                        if endstop[3].endswith("0"):
                            self.LimitZ = False
                elif trimLine.startswith("MachineStatus"):
                    if trimLine.endswith("READY"):
                        self.Status = machineStatus.Ready
                    elif trimLine.endswith("BUILDING_FROM_SD"):
                        self.Status = machineStatus.Building
                    else:
                        self.Status = machineStatus.Busy

    def UpdateTempStatus(self):
        """温度の情報を更新"""
        work = self.Send("M105")
        if self.IsOk(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(':|/|B', split[1].strip())
                if len(splitLine) == 6:
                    self.CurrentTempNozel = int(splitLine[1])
                    self.TargetTempNozel = int(splitLine[2])
                    self.CurrentTempBed = int(splitLine[4])
                    self.TargetTempBed = int(splitLine[5])
    
    def UpdateJobStatus(self):
        """JOB状態を更新"""
        work = self.Send("M27")
        if self.IsOk(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(' |/', split[1].strip())
                if len(splitLine) == 5:
                    self.SdProgress = int(splitLine[3])
                    self.SdMax = int(splitLine[4])

    def UpdatePosition(self):
        work = self.Send("M114")
        if self.IsOk(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(' |:', split[1].strip())
                if len(splitLine) == 10:
                    self.PosX = float(splitLine[1])
                    self.PosY = float(splitLine[3])
                    self.PosZ = float(splitLine[5])
                    self.PosE = float(splitLine[7])

    def UpdateStatus(self):
        """Adventurer3の情報の取り出し(更新)"""
        self.UpdateMachneStatus()
        self.UpdateTempStatus()
        self.UpdateJobStatus()
        self.UpdatePosition()

    def Led(self, OnOff):
        """LEDの表示・消去"""
        if OnOff == True:
            self.Send("M146 r255 g255 b255 F0")
        else:
            self.Send("M146 r0 g0 b0 F0")

    def StopJob(self):
        """JOB停止"""
        self.Send("M26")

    def Stop(self):
        """機器の緊急停止"""
        self.Send("M112")
        self.UpdatePosition()

    def GetStatus(self):
        return "ノズル {0}/{1}, ベッド {2}/{3}, 機器 {4}, 印刷 {5}/{6}, X:{7} Y:{8} Z:{9} E:{10}".\
        format(self.CurrentTempNozel, self.TargetTempNozel,
        self.CurrentTempBed, self.TargetTempBed,
        self.Status,
        self.SdProgress, self.SdMax,
        self.PosX, self.PosY, self.PosZ, self.PosE)