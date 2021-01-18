import marshmallow

from app.common.decorator import return_500_if_errors
from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from flask import request
import jwt

from app.students.form import StudentSchema
from config import SECRET_KEY, ACCESS_TOKEN_LIFE, REFRESH_TOKEN_LIFE
from datetime import datetime
from datetime import timedelta
import json
import requests


class Refresh(Resource):

    @return_500_if_errors
    def post(self):
        """
        refreshToken을 헤더에 넣어주면 accessToken을 재발급해준다.
        :return:
        200 : 정상적인 재발급
        400 : 토큰 미입력
        401 : 토큰 무효(만료)
        """

        if request.headers.get('Authorization') is None:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        refresh_token = request.headers.get('Authorization').split()
        if len(refresh_token) < 2:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        refresh_token = refresh_token[1]

        print(refresh_token)

        if refresh_token is not None:
            try:
                payload = jwt.decode(refresh_token, SECRET_KEY, "HS256")
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return {"message": "토큰이 유효하지 않습니다."}, 401



            if "refresh" not in payload or payload["refresh"] is not True:
                return {"message": "토큰이 유효하지 않습니다."}, 401

            payload.pop("refresh")
            payload["exp"] = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_LIFE)
            access_token = jwt.encode(payload, SECRET_KEY, "HS256").decode("UTF-8")

            return {
                "accessToken": access_token
            }

        else:

            return {"message": "로그인 토큰이 필요합니다."}, 400
