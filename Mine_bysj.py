# encoding:utf-8
from datetime import timedelta
from flask import Flask, render_template, request, make_response, redirect, \
    url_for, session, g
import os
import json
from uploader import Uploader
import re
import config
from models import *
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# 页面信息
page_content = {
    'nav_label': [],  # 标签列表,存储所有标签对象
    'select': 100  # 设置标签的选中状态
}

# 添加jinja的全局变量字典,自动更改
app.jinja_env.globals['session'] = session
app.jinja_env.globals['page_content'] = page_content  # 全局字典里的页面信息字典
app.jinja_env.auto_reload = True


# 用户密码MD5加密
def create_md5(str_passwd):
    import hashlib
    m = hashlib.md5()
    m.update(str_passwd.encode('utf8'))
    return m.hexdigest()


# 在app入栈后和请求前之间的操作
@app.before_request
def before_request():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        session_user = User.query.filter(User.id == user_id).first()
        if session_user:
            # app的全局变量g.user
            g.user = session_user
            page_content['nav_label'] = Label.query.filter().all()


@app.route('/')
@login_required
def index():
    index_article = Article.query.filter().order_by(Article.modify_time).offset(
        0).limit(14).all()
    return render_template('index.html', articles=index_article)


# 注册
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
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


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = create_md5(password)
        login_user = User.query.filter(User.username == username,
                                       User.password == password_hash).first()
        if login_user:
            session.permanent = True
            # 设置回话保存时间
            app.permanent_session_lifetime = timedelta(
                days=config.session_lifetime)
            session['user_id'] = login_user.id
            user_authority = UserAuthority.query.filter(
                UserAuthority.user == login_user).first()
            if user_authority:
                session['admin_id'] = login_user.id
            # 将用户名保存到页面信息
            page_content['username'] = login_user.username
            return redirect(url_for('index'))
        else:
            page_content['error'] = u'用户名或密码错误!'
            return render_template('error.html')


# 注销登录
@app.route('/logout')
@login_required
def logout():
    session.clear()
    page_content.clear()
    return redirect(url_for('index'))


# 添加笔记:
@app.route('/article/add', methods=['POST', 'GET'])
@login_required
def article_add():
    if request.method == 'GET':
        return render_template('article/add_article_ueditor.html')
    else:
        title = request.form.get('title')
        info = request.form.get('info')
        label_id = request.form.get('label_id')
        form_content = request.form.get('content')
        article_model = Article(title=title, info=info, content=form_content,
                                label_id=label_id, author_id=g.user.id)
        article_model.author = g.user
        db.session.add(article_model)
        db.session.commit()
        return redirect(url_for('index'))


# 编辑器上传接口
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


# 查看笔记列表
@app.route('/list/<label_id>', methods=['GET', 'POST'])
@login_required
def list(label_id):
    page_content['select'] = label_id
    kw = {
        'articles': Article.query.filter(Article.label_id == label_id).order_by(
            -Article.id).all(),
        'label_name': Label.query.filter(Label.id == label_id).first().name
    }
    if request.method == 'GET':
        return render_template('list.html', **kw)
    else:
        pass


# 查看笔记详情
@app.route('/article/<article_id>', methods=['GET', 'POST'])
@login_required
def article(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        if not article_model:
            page_content['error'] = u'文章不存在!'
            return render_template('error.html')
        return render_template('article.html', article=article_model)
    else:
        pass


# 删除笔记
@app.route('/article/delete/<article_id>', methods=['POST', 'GET'])
@login_required
def article_delete(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        db.session.delete(article_model)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        pass


# 修改笔记
@app.route('/article/edit/<article_id>', methods=['POST', 'GET'])
@login_required
def article_edit(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        return render_template('article/edit.html', article=article_model)
    else:
        title = request.form.get('title')
        info = request.form.get('info')
        label_id = request.form.get('label_id')
        form_content = request.form.get('content')
        article_model.title = title
        article_model.info = info
        article_model.content = form_content
        article_model.label_id = label_id
        article_model.modify_time = datetime.now()
        db.session.commit()
        return redirect(url_for('index'))



#修改标签
@app.route('/label/edit/<label_id>', methods=['GET', 'POST'])
@login_required
def label_edit(label_id):
    label = Label.query.filter(Label.id == label_id).first()

    if not label:
        page_content['error'] = u'标签不存在!'
        return render_template('error.html', **page_content)
    page_content['label'] = label
    if request.method == 'GET':
        all_label = Label.query.filter(Label.id != label_id).all()
        page_content['all_label'] = all_label
        return render_template('label/edit.html', **page_content)
    else:
        name = request.form.get('name')
        if name == '':
            page_content['error'] = u'标签名不能为空!'
            return render_template('error.html', **page_content)
        temp = Label.query.filter(Label.name == name).first()
        if temp and temp != label:
            page_content['error'] = u'已经存在该标签名!'
            return render_template('error.html', **page_content)
        parent_id = request.form.get('parent_id')
        label.name = name
        parent = Label.query.filter(Label.id == parent_id).first()
        label.parent = parent
        db.session.commit()
        return redirect(url_for('label_add'))

#增加标签
@app.route('/label/add', methods=['GET', 'POST'])
@login_required
def label_add():
    if request.method == 'GET':
        all_label = Label.query.all()
        page_content['all_label'] = all_label
        return render_template('label/add.html', **page_content)
    else:
        name = request.form.get('name')
        if name == '':
            page_content['error'] = u'标签名不能为空!'
            return render_template('error.html', **page_content)
        temp = Label.query.filter(Label.name == name).first()
        if temp:
            page_content['error'] = u'已经存在该标签名!'
            return render_template('error.html', **page_content)
        parent_id = request.form.get('parent_id')
        parent = Label.query.filter(Label.id == parent_id).first()
        label = Label(name=name)
        label.parent = parent
        db.session.add(label)
        db.session.commit()
        return redirect(url_for('label_add'))

#删除标签
@app.route('/label/delete/<label_id>')
@login_required
def label_delete(label_id):
    label = Label.query.filter(Label.id == label_id).first()
    if label:
        children_label = Label.query.filter(Label.parent_id == label_id).all()
        other_label = Label.query.filter(Label.name == '其他').first()
        for child in children_label:
            child.parent = other_label
        db.session.delete(label)
        db.session.commit()
    return redirect(url_for('label_add'))


if __name__ == '__main__':
    app.run()
