# -*- coding: utf-8 -*-
"""
Adventurer3に接続してそのステータスを表示するもの
"""
import Adventurer3.Controller
import io, threading, time
from datetime import datetime
from flask import (
    Blueprint, redirect, render_template, request, session, url_for, send_file,
    make_response, jsonify
)

bp = Blueprint('views', __name__)
bp.monitor = None

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    """ホームでの処理"""
    if request.method == 'POST':
        # IPアドレスを取得して、それをもってAdventurer3の制御用スレッドを起動する
        session['address'] = request.form['address']
        address = session['address']
        if len(address) > 0:
            bp.monitor = MonitoringAdventurer3(session['address'])
            bp.monitor.start()
            return redirect(url_for('views.display'))
        return redirect(url_for('views.home')) 
    else:
        # Adventurer3用の制御スレッドがあれば、いったん閉じる
        # その後、IP取得ページを表示する
        if bp.monitor != None:
           if bp.monitor.is_alive():
                bp.monitor.is_continue = False
                bp.monitor.join()
        bp.monitor = None
        return render_template(
            'index.html',
            title="Adventurer3 Control",
            year=datetime.now().year)

@bp.route('/display')
def display():
    """Adventurer3の状況表示"""
    # Adventurer3制御スレッドがあれば、モニター表示
    # なければIPアドレス指定ページの表示
    if bp.monitor != None and bp.monitor.is_alive():
        return render_template(
            'display.html',
            title="Adventurer3 Control",
            year=datetime.now().year)
    else:
        return redirect(url_for('views.home'))

@bp.route('/image.jpg')
def image():
    """Adventurer3の画像表示"""
    if bp.monitor != None and bp.monitor.image != None:
        return send_file(io.BytesIO(bp.monitor.image),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='image.jpg')
    else:
        return send_file('static/images/blank.jpg',
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='image.jpg')

@bp.route('/getStatus', methods=['POST'])
def get_status():
    """Adventurer3のステータスをJson形式で返す"""
    if bp.monitor != None and bp.monitor.is_alive():
        retBody = {
                "IsConnect" : True,
                "Status" : bp.monitor.target.status.name,
                "CurrentTempNozel" : bp.monitor.target.current_temp_nozel,
                "TargetTempNozel" : bp.monitor.target.target_temp_nozel,
                "CurrentTempBed" : bp.monitor.target.current_temp_bed,
                "TargetTempBed" : bp.monitor.target.target_temp_bed,
                "SdProgress" : bp.monitor.target.sd_progress,
                "SdMax" : bp.monitor.target.sd_max,
        }
    else:
        retBody = {
                "IsConnect" : False,
                "Status" : "",
                "CurrentTempNozel" : "",
                "TargetTempNozel" : "",
                "CurrentTempBed" : "",
                "TargetTempBed" : "",
                "SdProgress" : "",
                "SdMax" : "",
        }
    # 以下でjson形式のレスポンスデータが作製される
    return make_response(jsonify(retBody))

class MonitoringAdventurer3(threading.Thread):
    """Adventurer3の機器監視"""
    def __init__(self, hostname):
        self.target = Adventurer3.Controller.Controller(hostname)
        self.is_continue = False
        self.image = None
        return super().__init__()

    def run(self):
        self.is_continue = True
        while self.is_continue:
            try:
                if self.target.start():
                    self.target.update_status()
                    self.target.end()
                    self.image = Adventurer3.Controller.download_image(
                        self.target.hostname)
                else:
                    self.is_continue = False
                    break
                time.sleep(2)
            except:
                self.is_continue = False
