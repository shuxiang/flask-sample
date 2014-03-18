#! /usr/bin/env python
#coding=utf-8
from flask import Flask, Response, request, current_app, session, g#principal need session
from flaskext.principal import Principal, Permission, RoleNeed, Identity, identity_changed, identity_loaded

app = Flask(__name__)
app.debug = True
app.secret_key = 'i am session secret key'#for session

#load extension
principal = Principal(app)
#create a permission with a single Need, in this case a RoleNeed
admin_perm = Permission(RoleNeed('admin'))#可以使用该类的方法如union(other_perm)获得合并的权限

@app.route('/admin')
@admin_perm.require(401)
def do_admin_index():
    print dir(g)
    return Response('Only if you are admin, for admin view')

#另一种方式
@app.route('/test')
def do_test():
    with admin_perm.require(401):
        return Response('Only if you are admin, for test view')
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        #check username
        #......
        identity_changed.send(current_app._get_current_object(), identity=Identity(username))
        return 'login and identity'
    return u"""
            <form method='post' action='/login'>
                Name:<input type='text' name='username' /><br/>
                <input type='submit' value='submit' />
            </form>
            """
            
@app.route('/logout')
def logout():
    u"""
        
    """
    if 'identity.name' in session:
        session.pop('identity.name')
        session.pop('identity.auth_type')
    return 'pop session key: identity'

    
#create User info providers
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    #along identity get user: identity.name
    user = {'roles':['admin']}
    #for role in user['roles']:
    identity.provides.add(RoleNeed('admin'))
    identity.user = user
    
if __name__ == '__main__':
    app.run()
