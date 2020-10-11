import marshmallow

from app.common.decorator import return_500_if_errors
from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *
from app.common.function import *
from flask import request
import requests
import json

from datetime import datetime


class _Schools(Resource):
    @return_500_if_errors
    def get(self):
        school_name = request.args.get("schoolName")
        print(school_name)

        school_data_list = get_school_by_school_name(school_name)
        if school_data_list is None:
            return {"message": "학교를 찾을 수 없습니다."}, 404
        return {
            "data" : school_data_list
        }, 200



class _SchoolCode(Resource):
    @return_500_if_errors
    def get(self, school_code=None):
        if not school_code or school_code == "":
            return {"message": "학교코드가 입력되지 않았습니다."}, 400
        school_row = School.query.filter_by(verify_code=school_code).first()
        if school_row is None:
            return {"message": "학교를 찾을 수 없습니다."}, 404
        return {
                   "message": "학교코드가 일치합니다.",
                   "data": {
                       "schoolId": school_row.school_id,
                       "schoolName": school_row.name,
                       "schoolRegion": school_row.region,
                       "schoolAddress": school_row.address
                   }
               }, 200
        # if not school_id:
        #     return {"message": "학교ID가 입력되지 않았습니다."}, 400
        # school_code = request.args.get("schoolCode")
        # if school_code is None:
        #     return {"message": "학교코드가 입력되지 않았습니다."}, 400
        #
        # school_row = School.query.filter_by(school_id=school_id).first()
        # if school_row is None:
        #     return {"message": "학교를 찾을 수 없습니다."}, 404
        # if school_row.verify_code is None:
        #     return {"message": "학교 코드가 설정되지 않았습니다."}, 406
        # if school_row.verify_code != school_code:
        #     return {"message": "학교코드가 일치하지 않습니다."}, 401
        # return {
        #     "message" : "학교코드가 일치합니다."
        # }, 200
