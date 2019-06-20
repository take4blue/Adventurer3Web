# PythonでAdventurer3を制御
FlashForgeのAdventurer3を制御するプログラム。

最終的には、ローカルエリアにあるAdventurer3を、外部にあるスマフォで制御したい。

初めてのPythonプログラムなので、段階的に作成していく予定。

## 第1段階
ローカルエリア内にあるマシンのコンソール画面からの制御。

制御できるコマンドは、機器のステータス確認、緊急停止、印刷停止。

ここでの目的は、以前C#で作成したAdventurer3の制御プログラムの一部をPythonに移植し、始めたばかりのPythonのプログラミングになれること。

- 機能概要<br>
Console.pyをAdventurer3のIPアドレスを引数に起動すると、'> 'でコマンド入力待ちになる。<br>
ここでは、p、s、jobstop、qが入力でき、それぞれ、機器の状態確認、緊急停止、印刷停止、プログラム終了が実行される。
- プログラムの構成<br>
Console.pyがアプリケーションの起点となるモジュール。<br>
Adventurer3/Controller.pyが、Adventurer3との通信を行う通信モジュール。

## 第2段階
ローカルエリア内にあるマシンをwebベースでの監視

監視対象は、マシンのステータスと内蔵カメラ。

ここでの目的は、Raspberry Pi+Pythonを使い、WebベースでのAdventurer3監視機能を作成すること。

- 機能概要<br>
Raspberry Piで起動後、http://Raspberry PiのIP:8088 にアクセスすることで、サーバーに接続。<br>
IPアドレス指定画面と機器状態表示画面の2つの画面で構成される。
  - IPアドレス指定画面<br>
Adventurer3のIPアドレスを指定する。
  - 機器状態表示画面<br>
接続しているAdventurer3の状態と内蔵カメラで撮影した状態を表示する。
- プログラムの構成<br>
Adventurer3/views.pyがIPアドレス指定画面・機器状態表示画面を制御するためのコード。<br>
static以下のフォルダに入っているのは、htmlとそれに関連するファイル群。<br>
static以下は、基本的に、Visual StudioでPythonのWebプロジェクトを新規に作成した際に取り込まれたファイルになる。<br>
static/scripts/update.jsは機器状態表示画面で、Adventurer3の状態をサーバー側に問い合わせするためのスクリプトが入っている。<br>
InServer.pyはWebサーバーを起動するための起点となるモジュール。

### 起動方法
Raspberry Piにファイル類を持っていって、`Python3 InServer.py`で起動。<br>
ホスト名、ポートは、環境変数のSERVER_HOST、SERVER_PORTで指定できる。<br>
ホスト名の設定含め、次のように起動したほうがいいかもしれない。<br>
```sh
export SERVER_HOST=`hostname -I`
Python3 InServer.py
```

# License
This software is released under the MIT License, see LICENSE.txt.