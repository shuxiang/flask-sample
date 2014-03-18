#coding=utf-8
#import sqlalchemy
#print sqlalchemy.__version__
#
#from sqlalchemy import create_engine
#from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
#
#engine = create_engine('sqlite:///E:/sx/www/testsqla.db', echo=True)#创建数据库连接,echo=True使用logging模块产生sql输出
#
#metadata = MetaData()
#users_table = Table('users', metadata,
#        Column('id',Integer,primary_key=True),
#        Column('name',String),
#        Column('fullname',String),
#        Column('password',String)
#    )
#metadata.create_all(engine)#创建数据库
#
##使用这个类来定义对应的表的行为
#class User(object):
#    def __init__(self, name, fullname, password):
#        self.name = name
#        self.fullname = fullname
#        self.password = password
#        
#    def __repr__(self):
#        return u"<User('%s', '%s', '%s')>" % (self.name, self.fullname, self.password)
##映射类和表
#from  sqlalchemy.ext.declarative import mapper#,Table
#mapper(User, users_table
from sqlalchemy import Table,Column,Integer,String,MetaData,ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()#基类
class User(base):
    __tablename__ = 'users'
    
    id = Column(Integer,primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
        
    def __repr__(self):
        return u"<User('%s', '%s', '%s')>" % (self.name, self.fullname, self.password)

users_table = User.__table__#获取table
metadata = base.metadata    #获取metadata
engine = create_engine('sqlite:///E:/sx/www/testsqla.db', echo=True)#创建数据库连接,echo=True使用logging模块产生sql输出
metadata.create_all(engine) #创建数据库

#创建sqlalchemy session 来绑定一个数据库连接
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)# or create one: Session = sessionmaker(), 或者更改一个链接: Session.configure(bind=engine)
session = Session()

admin = User('admin','administrator','123456')
session.add(admin)
#print '@@@@@@@@admin id:',admin.id
gadmin = session.query(User).filter_by(name='admin').first()
#print '@@@@@@@@admin id:',admin.id#执行一个查询操作会导致前面的的事务被提交，id就改变了，不需要commit

#print gadmin
#print admin is gadmin#True
admin.password = '0000'#修改一个表对象属性
#print session.query(User).filter(User.name.in_(['admin'])).first()#in 操作, order_by(User.id)操作
#print '#########',session.dirty#查看被修改的数据（脏数据），session.new#查看新加入的数据
#session.add_all([
#        User('test','testuser','tttt'),
#        User('guest','guestuser','guest')
#    ])
#print session.query(User).all()
#session.add(gadmin)#重复对象加入不起作用
#print session.query(User).all()
#提交事务并应用改变到数据库，并释放连接到连接池。下次需要重新建立一个事务了
session.commit()#session.rollback()#回滚所有前面的操作
for name,fullname in session.query(User.name, User.fullname).filter_by(name='admin'):
    print name,'#',fullname

#filter_by(name='')类似filter(User.name==''),filter(name='')也是对的如果只query一个表
#也可以直接使用sql字符串:filter('id==20').order_by('id')等等
#也可以filter多个字段，AND, OR: 
#   from sqlalchemy import and_;filter(and_(User.name=='', User.email==''))
#不等于filter(User.name!=''); Like:filter(User.name.like(' %abc%'))
#IN: filter(User.name.in_(['admin','guest']); is null: filter(User.name==None)
#通过参数查询：
#   filter("id < :value and name=:name").params(value=22, name='admin')

#---------------------------------------------------------------------#
#-------多表----------------------------------------------------------#
from sqlalchemy.orm import relation, backref
class Address(base):
    __tablename__ = 'address'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    
    userid = Column(Integer, ForeignKey('users.id'))
    user  = relation(User, backref=backref('addresses', order_by=id))
    
    def __init__(self, email):
        self.email = email
        
    def __repr__(self):
        return u"<Address(' %s')>" % self.email
    
metadata.create_all(engine)
guest = User('guest','guest@gmail.com','pas')
print guest.addresses
guest.addresses = [Address('guest@g.com'),Address('guest@gmail.com')]
print guest.addresses[1].user
session.add(guest)
session.commit()

g1 = session.query(User).filter("name='guest'").first()#one()如果取回的数据不是一个，就会异常，所以最好用first()
print g1,g1.addresses
#多表查询
for u,a in session.query(User,Address).filter(User.id==Address.userid).all():
    print u,a
    
#join表查询
from sqlalchemy.orm import join
for ua in session.query(User).select_from(join(User,Address)).filter(Address.email=='guest@gmail.com').all():
    print ua#
#simple join    #多个join表的话： join(Foo.bars, Bar.bats,)
for ua in session.query(User).join(User.addresses).filter(Address.email=='guest@gmail.com').all():
    print ua
    
#print '\n',session.query(User).get(2)#by id
#session.query(User).filter_by(id=2).delete()
#print '\n',session.query(User).get(3)#by id
session.query(User).filter(User.name=='guest').delete()
print session.query(User).count()
print session.query(Address).count()

#from sqlalchemy.sql import func#, exists
#for u,c in session.query(Address.userid, func.count('*').label('address_count')).group_by(Address.userid):
#    print u,c
admin = User('admin','test',u'admin')
admin.addresses = [Address('guest@g.com'),Address('guest@gmail.com')]
session.add(admin)

#查指定的字段
for name,fullname,email in session.query(User.name, User.fullname, Address.email).filter(User.name=='admin').filter(Address.userid==User.id):
    print name,'#',fullname,'#',email

#通过别名访问数据
from sqlalchemy.orm import aliased
alias = aliased(User,name='user_alias')
for row in session.query(alias, alias.name.label('name_label')).all():
    print row.user_alias, row.name_label
    
#切片操作, 从第二条开始，取3条（即到第五条）, limit 3 offset 2
for u in session.query(User).order_by(User.id)[2:5]:
    print u
    
#一次取回user和addresses，不用查两次数据库
from sqlalchemy.orm import eagerload
print session.query(User).options(eagerload('addresses')).filter_by(name='admin').first()

#选择外键符合条件的任何记录, any用于一对多，多对多, (多对一，一对一应该用has???)
#for name in session.query(User.name).filter(User.addresses.any()):
#    print name
for name in session.query(User.name).filter(User.addresses.any(Address.email.like('%gmail%'))):
    print name

"""
for nn in User.query.filter(...).values(User.nickname):#这是一个生成器
    print nn#这是一个tuple
    
User.query.filter(...).value(User.nickname)#返回一个字段, 似乎只返回一个user的nickname
"""

print 'last'
for email,id in session.query(Address.email, Address.id).filter(Address.user.has(User.fullname=='test')).all():
    pass#print email,id

print session.query(Address.email, Address.id).filter(Address.user.has(User.fullname=='test')).all()

pagin = pagin.order_by(db.select([Item.hot]).where(Item.id==ActItem.item_id))

#filtering-by-relation-count
#query.filter( User.addresses.any())

#order_by first, then group_by
UserMailRelation.query.select_from(UserMailRelation.query.order_by('createtime desc').subquery()) \
            .group_by(UserMailRelation.from_id, UserMailRelation.to_id).filter(...)
            
###powerful join on statement
q = session.query(User).join(Address, User.id==Address.user_id)
###powerful join statement, subq join
    address_subq = session.query(Address).\
        filter(Address.email_address == ’ed@foo.com’).\
        subquery()
    q = session.query(User).join(address_subq, User.addresses)
#Producing SQL similar to:
    SELECT user.* FROM user
        JOIN (
        SELECT address.id AS id,
        address.user_id AS user_id,
        address.email_address AS email_address
        FROM address
        WHERE address.email_address = :email_address_1
    ) AS anon_1 ON user.id = anon_1.user_id
#The above form allows one to fall back onto an explicit ON clause at any time:
    q = session.query(User).\
    join(address_subq, User.id==address_subq.c.user_id)


#complicate union select
query = Tweet.query
query1 = query.join(Follow, Tweet.user_id==Follow.fo_id) \
                .filter(Follow.user_id==g.user.id).subquery().select()
query2 = query.filter(Tweet.user_id==g.user.id).subquery().select()
        
query = query.select_from(query1.union(query2)).order_by(Tweet.updatetime.desc())
# query.union(query1).union(query2)

# query multi
vlans = db.session.query(Vlan, Subnet.name).join(Subnet).order_by(Vlan.id)

# create table t4(id integer primary key,pwd varbinary(1000));
# insert into t4(id, pwd) values(1,ENCODE('abc','123'));
# select t4.id, decode(pwd,'123') as t4.pwd from t4  where INSTR(DECODE(pwd,'123'), 'bc') > 0;
T4.query.filter(db.func.instr(db.func.decode(T4.pwd,'123'),'ab')).all()
T4._pwd = db.column_property(db.select([db.func.decode(T4.pwd, '123')]).where(...), deferred=True)
