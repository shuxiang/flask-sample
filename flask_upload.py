#! /usr/bin/env python
#coding=utf-8

from flask import Flask, request, render_template
import hashlib,random,os.path
app = Flask(__name__)
app.debug = True#for debug

app.config['UPLOADED_FILES_DEST'] = './static/uploads'
app.config['UPLOADED_FILES_URL']  = '/static/uploads/'#need trailing slash
#upload set
from flaskext.uploads import UploadSet, IMAGES, configure_uploads
photos = UploadSet('photos', IMAGES, default_dest=lambda app:app.config['UPLOADED_FILES_DEST'])
configure_uploads(app, photos)


from wtforms import Form, BooleanField, TextField, IntegerField, SelectField, validators, FileField

class MyForm(Form):
    title = TextField(u'标题',[validators.Length(min=3, max=10, message=u"我擦，太长了")])
    num = IntegerField(u'数字', [validators.NumberRange(min=0, max=1000, message=u'请输入一个数字')])
    photo = FileField(u'文件')#, [validators.Required()])
    
    
@app.route("/upload", methods=['GET','POST'])
def upload():
    form = MyForm(request.form)
    if request.method == 'POST' and form.validate() and 'photo' in request.files and request.files['photo'].filename is not None:
        hashname = hashlib.md5(request.files['photo'].filename + str(random.random())).hexdigest()#sha1,sha224,sha256
        filename = photos.save(request.files['photo'], name=hashname+os.path.splitext(request.files['photo'].filename)[1])
        return 'uploaded'
    
    return render_template('uploadform.html', form=form)

if __name__ == "__main__":
    app.run()
