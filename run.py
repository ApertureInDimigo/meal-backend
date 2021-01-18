#!/usr/bin/env python
from app import create_app
from flask import render_template
from datetime import datetime
# app = create_app('config')
# app.app_context().push()

from app.db import db
app = create_app('config')
# db.create_all(app=app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.close()

# routing > react_router (method = GET)
@app.route('/', defaults={'path': ''}, methods=['GET'])
# @app.route('/<string:path>', methods=['GET'])
def catch_all(path):

    return render_template('./index/index.html')

@app.route('/privacy')
def privacy():

    return render_template('privacy.html')


@app.route('/app-ads.txt')
def app_ads():
    f = open('./app-ads.txt', 'r')
    ## 단 리턴되는 값이 list형태의 타입일 경우 문제가 발생할 수 있음.
    ## 또한 \n이 아니라 </br>으로 처리해야 이해함
    ## 즉 파일을 읽더라도 이 파일을 담을 html template를 만들어두고, render_template 를 사용하는 것이 더 좋음
    return "</br>".join(f.readlines())



@app.route('/password-reset')
def password_reset_template():

    return render_template('./mail/password_reset.html', data={"verify_code" : "123456"})


# 404 not found > react_router
@app.errorhandler(404)
def not_found(error):
    print("SDF")


    return render_template('index.html')






if __name__ == '__main__':

    print(datetime.now())

    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
