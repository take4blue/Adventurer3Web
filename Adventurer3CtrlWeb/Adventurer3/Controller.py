# -*- coding: utf-8 -*-
import socket
import requests
import re
from enum import Enum

class MachineStatus(Enum):
    Ready = 0
    Busy = 1
    Building = 2
    Transfer = 3

class Controller(object):
    """Adventurer3との通信用制御クラス"""

    DEFAULT_PORT = 8899  # Adventurer3への接続ポート番号(一応固定)

    def __init__(self, hostname):
        """コンストラクタ"""
        self.hostname = hostname
        self.status = None
        self.current_temp_bed = 0
        self.current_temp_nozel = 0
        self.target_temp_bed = 0
        self.target_temp_nozel = 0
        self.sd_max = 100
        self.sd_progress = 0
        self.limit_x = False
        self.limit_y = False
        self.limit_z = False
        self.pos_e = 0
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0

    def start(self):
        """
        Adventurer3との接続開始
        間違ったIPを指定すると、この関数のリターンにすごく時間がかかる場合がある。
        (タイムアウトまで待つため）
        """
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.connect((self.hostname, self.DEFAULT_PORT))
        except OSError:
            return False
        self.tcp.send("~M601 S1\r\n".encode())
        self.recv()
        return True

    def end(self):
        """Adventurer3との接続解除"""
        if self.is_connected:
            self.tcp.send("~M602 S1\r\n".encode())
            self.recv()
            self.tcp.close()
            self.tcp = None

    def recv(self):
        """データの受信"""
        data = self.tcp.recv(4096)
        if not data:
            return None
        else:
            return data.decode('utf-8')

    def send(self, data):
        """データの送信"""
        if self.is_connected:
            sendData = "~" + data
            try:
                self.tcp.send(sendData.encode())
                return self.recv()
            except OSError:
                return ""

    def is_connected(self):
        """Adventurer3と接続中かどうか"""
        if not self.tcp:
            return False
        else:
            return True

    def is_ok(self, data):
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

    def update_machine_status(self):
        """機器の状態取得"""
        work = self.send("M119")
        if self.is_ok(work):
            split = work.split("\n")
            for line in split:
                trimLine = line.strip()
                if trimLine.startswith("Endstop"):
                    endstop = trimLine.split(' ')
                    if len(endstop) == 4:
                        self.limit_x = self.limit_y = self.limit_z = True
                        if endstop[1].endswith("0"):
                            self.limit_x = False
                        if endstop[2].endswith("0"):
                            self.limit_y = False
                        if endstop[3].endswith("0"):
                            self.limit_z = False
                elif trimLine.startswith("MachineStatus"):
                    if trimLine.endswith("READY"):
                        self.status = MachineStatus.Ready
                    elif trimLine.endswith("BUILDING_FROM_SD"):
                        self.status = MachineStatus.Building
                    else:
                        self.status = MachineStatus.Busy

    def update_temp_status(self):
        """温度の情報を更新"""
        work = self.send("M105")
        if self.is_ok(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(':|/|B', split[1].strip())
                if len(splitLine) == 6:
                    self.current_temp_nozel = int(splitLine[1])
                    self.target_temp_nozel = int(splitLine[2])
                    self.current_temp_bed = int(splitLine[4])
                    self.target_temp_bed = int(splitLine[5])
    
    def update_job_status(self):
        """JOB状態を更新"""
        work = self.send("M27")
        if self.is_ok(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(' |/', split[1].strip())
                if len(splitLine) == 5:
                    self.sd_progress = int(splitLine[3])
                    self.sd_max = int(splitLine[4])

    def update_position(self):
        work = self.send("M114")
        if self.is_ok(work):
            split = work.split("\n")
            if len(split) >= 3:
                splitLine = re.split(' |:', split[1].strip())
                if len(splitLine) == 10:
                    self.pos_x = float(splitLine[1])
                    self.pos_y = float(splitLine[3])
                    self.pos_z = float(splitLine[5])
                    self.pos_e = float(splitLine[7])

    def update_status(self):
        """Adventurer3の情報の取り出し(更新)"""
        self.update_machine_status()
        self.update_temp_status()
        self.update_job_status()
        self.update_position()

    def led(self, OnOff):
        """LEDの表示・消去"""
        if OnOff == True:
            self.send("M146 r255 g255 b255 F0")
        else:
            self.send("M146 r0 g0 b0 F0")

    def stop_job(self):
        """JOB停止"""
        self.send("M26")

    def stop(self):
        """機器の緊急停止"""
        self.send("M112")
        self.update_position()

    def get_status(self):
        return "ノズル {0}/{1}, ベッド {2}/{3}, 機器 {4}, 印刷 {5}/{6}, X:{7} Y:{8} Z:{9} E:{10}".\
        format(self.current_temp_nozel, self.target_temp_nozel,
        self.current_temp_bed, self.target_temp_bed,
        self.status,
        self.sd_progress, self.sd_max,
        self.pos_x, self.pos_y, self.pos_z, self.pos_e)

def download_image(address, timeout = 10):
    """Adventurer3からカメラの静止画画像を取得する"""
    url = 'http://' + address + ':8080/?action=snapshot'
    response = requests.get(url, allow_redirects=False, timeout=timeout)
    if response.status_code != 200:
        e = Exception("HTTP status: " + response.status_code)
        raise e

    content_type = response.headers["content-type"]
    if 'image' not in content_type:
        e = Exception("Content-Type: " + content_type)
        raise e

    return response.content
