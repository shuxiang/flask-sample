from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://:memory:'#'sqlite://E:/sx/www/test.db'#error
app.config['DATABASE_URI'] = 'sqlite:///:memory:'
#app.config['DATABASE_URI'] = 'sqlite://E:/sx/www/test.db'
db = SQLAlchemy(app)


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
#if want to use in shell, must use this #app.test_request_context().push()
#filter_by return a BaseQuery object, use 'first' or other method to get models object

article_tags = db.Table('t_article_tags',db.Model.metadata,#db.MetaData(),
                db.Column('tag_id', db.Integer, db.ForeignKey('t_tag.id',ondelete='CASCADE'), primary_key=True),
                db.Column('article_id', db.Integer, db.ForeignKey('t_article.id',ondelete='CASCADE'), primary_key=True)
        )

class Article(db.Model):
    __tablename__ = 't_article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    content = db.Text()
    
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'))
    tags = db.relation('Tag', secondary=article_tags, backref='articles', lazy='dynamic')

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

    def __repr__(self):
        return '<Article %r>' % self.title[10]

class Tag(db.Model):
    __tablename__ = 't_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    count = db.Column(db.Integer)
    
    def __init__(self, name, count):
        self.name = name
        self.count = count
    
    def __repr__(self):
        return '<Tag %r>' % self.name
    
db.create_all()

u1 = User(username='admin',email='29@gmail.com')
db.session.add( u1)
db.session.commit()

a1 = Article(title='title1',content='c1', user_id=u1.id)
a2 = Article(title='title2',content='c2', user_id=u1.id)
db.session.add(a1)
db.session.add(a2)
db.session.commit()

t1 = Tag(name='t1',count=0)
t2 = Tag(name='t2',count=0)
db.session.add(t1)
db.session.add(t2)
db.session.commit()

a1.tags = [t1,t2]
db.session.add(a1)
db.session.commit()

t1.articles = [a1,a2]
db.session.add(t1)
db.session.commit()

with app.test_request_context():
    print Tag.query.all()
    print Tag.query.filter(Tag.articles.any(Article.id==1)).first()
