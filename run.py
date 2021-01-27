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

@app.route('/', defaults={'path': ''}, methods=['GET'])
def catch_all(path):

    return render_template('./index/index.html')

@app.route('/privacy')
def privacy():

    return render_template('privacy.html')


@app.route('/app-ads.txt')
def app_ads():
    f = open('./app-ads.txt', 'r')
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
