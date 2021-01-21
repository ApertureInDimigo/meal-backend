import threading

import marshmallow

from app.common.decorator import return_500_if_errors, login_required
from app.common.function import send_mail, get_identify

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *

from flask import request, render_template
import requests
import json

from datetime import datetime
from app.redis import rd
from config import SECRET_KEY

class IdCheck(Resource):
    @return_500_if_errors
    def get(self, id):
        """
        id 중복 체크
        :param id:
        :return:
        200 : 사용 가능
        409 : 중복
        """


        # id = request.args.get("id")
        c = Student.query.filter_by(id=id).count()
        if c != 0:
            return {"message": "이미 존재하는 ID 입니다."}, 409
        else:
            return {"data":
                {
                    "id": id
                },
                       "message": "사용 가능한 ID입니다."
                   }, 200