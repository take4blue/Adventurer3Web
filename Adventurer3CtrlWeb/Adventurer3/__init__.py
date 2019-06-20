# -*- coding: utf-8 -*-
"""
初期化処理
"""
from flask import Flask

def create_app(test_config=None):
    # トップアプリケーションオブジェクトの作成
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import views
    app.register_blueprint(views.bp)    # 制御用のページ登録
    return app
