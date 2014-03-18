#! /usr/bin/env python
#coding=utf-8

from flask import Flask, request, render_template
app = Flask(__name__)
app.debug = True#for debug

from flaskext.sqlalchemy import SQLAlchemy
#noworking for sqlalchemy:
#app.config['DATABASE_URI'] = "mysql://root:root@localhost:3306/test"#'sqlite:///E:/sx/www/sqlform.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/sx/www/sqlform.db'
db = SQLAlchemy(app)



from wtforms import Form, BooleanField, TextField, IntegerField, SelectField, validators
class MyForm(Form):
    username = TextField(u'姓名',[validators.Length(min=3, max=10, message=u"长度3到10位")])
    email = TextField(u'邮箱', [validators.Email( message=u'输入正确的邮箱地址')])
    """
    instance is form: str(form.username) is <input ....
    form.username(width='200px',style='..') can set some attr
    """
    
@app.route("/", methods=['GET','POST'])
def hello():
    form = MyForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(**form.data)
        db.session.add(user)
        db.session.commit()
        u1 = User.query.all()[0]
        print repr(u1)
    
    return render_template('testform.html', form=form)

@app.route('/edit/<int:id>/', methods=['GET','POST'])
def edit(id):
    user = User.query.get_or_404(id)
    form = MyForm(request.form, user)    
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        db.session.add(user)#add方法，如果对象有id，则是update操作
        ##paginate(page, per_page, echo_error=True)
        ##page is 当前页，per_page is 每页条数， echo_error is 不满足条件时是否raise错误
        ##pagin.items可以的到当前页的条目
        ##has_next/prev是否有上下页，next()/prev()获取上下页
        return 'update succeed!!!'

    return render_template('testform.html', form=form)

##test
class User(db.Model):
    __tablename__ = 't_user'#must need
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

##end test

if __name__ == "__main__":
    db.engine.echo = True
    db.create_all()
    app.run()
