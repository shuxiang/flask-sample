#! /usr/bin/env python
#coding=utf-8

from flask import Flask, request, render_template, g
app = Flask(__name__)
app.debug = True#for debug

from wtforms import Form, BooleanField, TextField, IntegerField, SelectField, validators
class MyForm(Form):
    title = TextField(u'标题',[validators.Length(min=3, max=10, message=u"我擦，太长了")])
    num = IntegerField(u'数字', [validators.NumberRange(min=0, max=1000, message=u'请输入一个数字')])
    choice = BooleanField(u'请选择', [validators.Required(message=u'必须选择？')])
    yesno = SelectField(u'单选一', [], choices=[('0','---'),('1',u'是'),('2',u'否')])
    
@app.route("/", methods=['GET','POST'])
def hello():
    form = MyForm(request.form)
    print dir(form)
    if request.method == 'POST' and form.validate():
        return 'ok!!!!!!!'
    
    return render_template('testform.html', form=form)

#@app.before_request
#def before():
#    g.aa = 222
#
#@app.after_request
#def after(resp):
#    print g.aa
#    return resp


if __name__ == "__main__":
    app.run()
