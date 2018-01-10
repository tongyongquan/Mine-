#encoding:utf-8
from flask import Flask,render_template,url_for
from exts import db
import config

app=Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    return render_template('base.html')



if __name__ == '__main__':
    app.run()
