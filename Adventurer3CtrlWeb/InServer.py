# -*- coding: utf-8 -*-
from os import environ
from Adventurer3 import create_app

app = create_app()

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '8088'))
    except ValueError:
        PORT = 8088
    app.run(HOST, PORT)
