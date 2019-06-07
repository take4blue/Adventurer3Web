import sys
import gettext
import Adventurer3.Controller

gettext.install(__name__)

class App:
    """UIアプリケーションクラス"""

    def __init__(self, ipaddress):
        self.adv3 = Adventurer3.Controller.Controller(ipaddress)

    def Ui(self):
        while True:
            cmd = input("> ").strip()
            if cmd.startswith("q") or cmd.startswith("Q"):
                break
            if cmd.startswith("p") or cmd.startswith("P"):
                if self.adv3.Start():
                    self.adv3.UpdateStatus()
                    self.adv3.End()
                    print(self.adv3.GetStatus())
            if cmd.startswith("s") or cmd.startswith("s"):
                if self.adv3.Start():
                    self.adv3.Stop()
                    self.adv3.End()
            if cmd.startswith("jobstop"):
                if self.adv3.Start():
                    self.adv3.StopJob()
                    self.adv3.End()

if __name__ == "__main__":
    """引数はホスト名かIPアドレスと仮定して処理をする"""
    if len(sys.argv) > 1:
        app = App(sys.argv[1])
        app.Ui()