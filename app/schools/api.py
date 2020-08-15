import marshmallow

from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *
from werkzeug import ImmutableMultiDict
from flask import request
import requests
import json

from datetime import datetime


class _Schools(Resource):

    def get(self):
        school_name = request.args.get("schoolName")
        print(school_name)
        url = f"https://open.neis.go.kr/hub/schoolInfo?&SCHUL_NM={school_name}&Type=json"
        response = requests.request("GET", url)

        school_data = json.loads(response.text)

        if "schoolInfo" not in school_data:
            return {"message": "학교를 찾을 수 없습니다."}, 404

        school_data_list = school_data["schoolInfo"][1]["row"]
        return {
            "data": [{
                "schoolId": school_data["SD_SCHUL_CODE"],
                "schoolName": school_data["SCHUL_NM"],
                "schoolAddress": school_data["ORG_RDNMA"],
                "schoolRegion": school_data["LCTN_SC_NM"]
            } for school_data in school_data_list]
        }


class _SchoolCode(Resource):

    def get(self, school_id = None):
        if not school_id:
            return {"message": "학교ID가 입력되지 않았습니다."}, 400
        school_code = request.args.get("schoolCode")
        if school_code is None:
            return {"message": "학교코드가 입력되지 않았습니다."}, 400

        school_row = School.query.filter_by(school_id=school_id).first()
        if school_row is None:
            return {"message": "학교를 찾을 수 없습니다."}, 404
        if school_row.verify_code is None:
            return {"message": "학교 코드가 설정되지 않았습니다."}, 406
        if school_row.verify_code != school_code:
            return {"message": "학교코드가 일치하지 않습니다."}, 401
        return {
            "message" : "학교코드가 일치합니다."
        }, 200