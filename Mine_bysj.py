# encoding:utf-8
from datetime import timedelta
from flask import Flask, render_template, request, make_response,redirect,url_for,session,g
from exts import db
import os
import json
from uploader import Uploader
import re
import config
from models import *




app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# 添加jinja的全局变量 session
app.jinja_env.globals['session'] = session
app.jinja_env.auto_reload = True


# 网页模板的参数(页面信息)
def get_page_content():
    page_content = {
    }
    # 设置导航栏标签的选项
    to_nav_label(page_content)
    return page_content


# nav 设置导航栏的选项
def to_nav_label(page_content):
    nav_label = Label.query.filter(Label.parent_id.is_(None)).all()
    page_content['nav_label'] = nav_label

#用户密码MD5加密
def create_md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

@app.before_request
def before_request():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        session_user = User.query.filter(User.id == user_id).first()
        if session_user:
            g.user = session_user

@app.route('/')
def index():
    page_content = get_page_content()
    return render_template('base.html', **page_content)


#注册
@app.route('/register',methods=['POST','GET'])
def register():
    page_content = get_page_content()

    if request.method=='GET':
        return  render_template('register.html')
    else:
        page_content['error'] = u'验证码错误!'

        username = request.form.get('username')
        password = request.form.get('password')
        if username == '' or password == '':
            page_content['error'] = u'用户名或密码为空!'
            return render_template('error.html', **page_content)
        re_password = request.form.get('re_password')
        if password != re_password:
            page_content['error'] = u'两次密码不一致!'
            return render_template('error.html', **page_content)
        # avatar = request.form.get('avatar')
        register_user = User.query.filter(User.username == username).first()
        if register_user:
            page_content['error'] = u'用户已存在!'
            return render_template('error.html', **page_content)
        register_user = User(username=username, password=create_md5(password))
        del page_content['error']
        db.session.add(register_user)
        db.session.commit()
        return redirect(url_for('login'))


#登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    page_content = get_page_content()
    if request.method == 'GET':
        return render_template('login.html', **page_content)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = create_md5(password)
        login_user = User.query.filter(User.username == username, User.password == password_hash).first()
        if login_user:
            session.permanent = True
            #设置回话保存时间
            app.permanent_session_lifetime = timedelta(days=config.session_lifetime)
            session['user_id'] = login_user.id
            user_authority = UserAuthority.query.filter(UserAuthority.user == login_user).first()
            if user_authority:
                session['admin_id'] = login_user.id
            #将用户名保存到页面信息
            page_content['username']=login_user.username
            return redirect(url_for('index'))
        else:
            page_content['error'] = u'用户名或密码错误!'
            return render_template('error.html', **page_content)

#注销登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#添加笔记:
@app.route('/article/add', methods=['POST', 'GET'])
#@login_required
def article_add():
    if request.method == 'GET':
        page_content = get_page_content()
        all_label = Label.query.all()
        page_content['all_label'] = all_label
        return render_template('article/add_article_ueditor.html',**page_content)
    else:
        title = request.form.get('title')
        info = request.form.get('info')
        label_id = request.form.get('label_id')
        form_content = request.form.get('content')
        article_model = Article(title=title, info=info, content=form_content, label_id=label_id,author_id=g.user.id)
        article_model.author = g.user
        db.session.add(article_model)
        db.session.commit()
        return redirect(url_for('index'))




#编辑器上传接口
@app.route('/upload/', methods=['GET', 'POST', 'OPTIONS'])
def upload():
    """UEditor文件上传接口

    config 配置文件
    result 返回结果
    """
    mimetype = 'application/json'
    result = {}
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(app.static_folder, 'ueditor', 'php',
                           'config.json')) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, app.static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, app.static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = '请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = json.dumps({'state': 'callback参数不合法'})

    res = make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers[
        'Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res







if __name__ == '__main__':
    app.run()
