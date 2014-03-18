#! /usr/bin/env python
#coding=utf-8

from flask import Flask, request, render_template
from flaskext.cache import  Cache
app = Flask(__name__)
app.debug = True#for debug

app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60*30

cache = Cache(app)#?cache.init_app(app)

@app.route("/")
@cache.cached()#这个装饰器必须放在app.route的下面#
def hello():
    from datetime import datetime
    return repr(datetime.now())

if __name__ == "__main__":
    app.run()
