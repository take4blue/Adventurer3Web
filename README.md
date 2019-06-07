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

# License
This software is released under the MIT License, see LICENSE.txt.