# -*- coding: utf-8 -*-
import sys
import gettext
import Adventurer3.Controller

gettext.install(__name__)

class App:
    """UIアプリケーションクラス"""

    def __init__(self, ipaddress):
        self.adv3 = Adventurer3.Controller.Controller(ipaddress)

    def user_interface(self):
        while True:
            cmd = input("> ").strip()
            if cmd.startswith("q") or cmd.startswith("Q"):
                break
            if cmd.startswith("p") or cmd.startswith("P"):
                if self.adv3.start():
                    self.adv3.update_status()
                    self.adv3.end()
                    print(self.adv3.get_status())
            if cmd.startswith("s") or cmd.startswith("s"):
                if self.adv3.start():
                    self.adv3.stop()
                    self.adv3.end()
            if cmd.startswith("jobstop"):
                if self.adv3.start():
                    self.adv3.stop_job()
                    self.adv3.end()

if __name__ == "__main__":
    """引数はホスト名かIPアドレスと仮定して処理をする"""
    if len(sys.argv) > 1:
        app = App(sys.argv[1])
        app.user_interface()