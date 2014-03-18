#! /usr/bin/env python
#coding=utf-8

from flask import Flask, current_app
app = Flask(__name__)
app.debug = True#for debug
app.secret_key = 'i am session secret key'#for session

#logging test
from logging import FileHandler,Formatter
file_handler = FileHandler(filename='app.log',encoding='utf-8')
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)



from flask import url_for
from flask import request, make_response, session, g, redirect
from flask import flash, get_flashed_messages

#g全局对象不能跨请求使用，但能直接在模板里使用，如{{ g.attr }}，和request一样是局部上下文对象，见quickstart
##test
@app.before_request
def before():
    g.aa = 222
    print request.form

@app.after_request
def after(resp):
    print g.aa
    return resp
##end test

@app.route("/")
def hello():
    print g.aa
    app.logger.debug('a value for debug')
    return "Hello, Flask!"

@app.route("/str/<strarg>/")
def strargtest(strarg):
    print g.aa
    return strarg

@app.route("/int/<int:intarg>/")
def intargtest(intarg):
    flash('####test flash')#flash，只能在下一个请求中使用一次，能在redirect中使用
    return redirect('/path/abc/')
    #return unicode(intarg)

@app.route("/path/<path:patharg>/")
def pathargtest(patharg):
    for msg in get_flashed_messages():
        print msg
    return patharg

@app.route("/m/", methods=['GET','POST'])
def methodtest():
#    if request.method == 'GET':
#        return 'get'
#    return "<br/>".join(dir(request))
    if request.method == 'POST':
        return request.form['tv']
    return """<form action='/m/' method='post'>
                <input type='text' value='122' name='tv' />
                <input type='submit' value='submit' />
            </form>
            <img src='/static/abc.jpg' />
            """+'<br/>'+request.args.get('q','nothing')
            
@app.route('/cookie/')
def cookietest():
    resp = make_response('')
    resp.set_cookie('name', 'abc')
    return resp#must return resp obj, 

@app.route('/viewcookie/')
def viewcookietest():
    return str(request.cookies)

@app.route('/sess/')
def sessiontest():
    session['mtv'] = u'ssss'
    return 'session test'

@app.route('/vsess/')
def vsess():
    return session['mtv']

if __name__ == "__main__":
    with app.test_request_context():    
        url_for("hello", next="/int/222/")
    app.run()
