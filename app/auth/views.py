from flask import Blueprint

from flask_restful import Api, Resource, reqparse


from app.auth.api.Auth import Auth
from app.auth.api.KakaoLogin import KakaoLogin
from app.auth.api.KakaoRegister import KakaoRegister
from app.auth.api.Refresh import Refresh

auth_bp = Blueprint('auth', __name__)

api = Api(auth_bp)


api.add_resource(Auth, '')
api.add_resource(Refresh, '/refresh')
api.add_resource(KakaoLogin, '/kakao/login')
api.add_resource(KakaoRegister, '/kakao/register')