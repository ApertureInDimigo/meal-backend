import jwt

from functools  import wraps
from flask 		import request, Response, g
from config import SECRET_KEY

def login_required(f):      									# 1)
    @wraps(f)                   								# 2)
    def decorated_function(*args, **kwargs):

        if request.headers.get('Authorization') is None:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = request.headers.get('Authorization').split()
        if len(access_token) < 2:
            return {"message": "로그인 토큰이 필요합니다."}, 400
        access_token = access_token[1]

        if access_token is not None:  							# 4)
            try:

                payload = jwt.decode(access_token, SECRET_KEY, 'HS256') 				   # 5)
            except jwt.InvalidTokenError:
                 payload = None     							# 6)

            if payload is None: return {"message": "토큰이 유효하지 않습니다."}, 401

            user_id   = payload["data"]["id"] 					# 8)
            g.user_id = user_id

        else:
            return {"message": "토큰이 유효하지 않습니다."}, 401					# 9)

        return f(*args, **kwargs)
    return decorated_function