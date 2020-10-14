import jwt

from functools import wraps
from flask import request, Response, g, jsonify
from config import SECRET_KEY
from app.common.function import *

import asyncio


def login_required(f):  # 1)
    @wraps(f)  # 2)
    def decorated_function(*args, **kwargs):

        if request.headers.get('Authorization') is None:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = request.headers.get('Authorization').split()
        if len(access_token) < 2:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = access_token[1]

        if access_token is not None:  # 4)
            try:

                payload = jwt.decode(access_token, SECRET_KEY, 'HS256')  # 5)
            except jwt.InvalidTokenError:
                payload = None  # 6)

            if payload is None: return {"message": "토큰이 유효하지 않습니다."}, 401

            user_id = payload["data"]["id"] if payload["data"]["type"] == "normal" else payload["data"]["kakaoId"]
            user_seq = payload["data"]["userSeq"]
            g.user_seq = user_seq
            g.user_id = user_id

        else:
            return {"message": "토큰이 유효하지 않습니다."}, 401  # 9)

        return f(*args, **kwargs)

    return decorated_function


import traceback
import requests
from datetime import datetime
import threading
import socket
import os


def return_500_if_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:

            print(traceback.print_exc())
            if is_local():
                return {
                           "message": "error"
                       }, 500

            print(f)
            error_message = traceback.format_exc()
            ip_address = request.headers[
                'X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else request.remote_addr
            print(json.dumps(request.get_json()) or "null")
            webhook_body = {

                "embeds": [
                    {
                        "title": "=========ERROR=========",
                        "color": 14177041

                    },
                    {
                        "fields": [
                            {
                                "name": "Function",
                                "value": str(f),
                                "inline": True
                            },
                            {
                                "name": "URI",
                                "value": request.url,
                                "inline": True
                            },
                            {
                                "name": "Request Body",
                                "value": json.dumps(request.get_json()) or "null"
                            },

                        ],
                        "color": 0

                    },
                    {
                        "description": error_message,
                        "color": 14177041
                    },
                    {
                        "title": str(datetime.now()) + ", " + (
                            "로컬에서 발생" if is_local() else "외부에서 발생") + ", " + ip_address,
                        "color": 0
                    },

                ]
            }
            threading.Thread(target=lambda: send_discord_webhook(webhook_body=webhook_body)).start()

            response = {
                "message": "error"
            }

            return response, 500

    return wrapper
