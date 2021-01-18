import firebase_admin
import marshmallow
import os
from PIL import Image
import uuid
from app.board.form import MealBoardSchema, MealBoardGetListSchema
from app.common.decorator import login_required, return_500_if_errors
from app.common.function import get_day_meal, get_identify
from app.db import *
from flask_restful import Resource, reqparse
import bcrypt
from marshmallow import Schema, fields, pprint, validate
from app.students.form import *
from flask import request, g, abort
import requests
import json
from app.common.function import *

from datetime import datetime
from sqlalchemy import func, desc

from app.scheduler import sched
from app.redis import rd
import datetime, time


class MealBoardLikeMy(Resource):

    @return_500_if_errors
    @login_required
    def get(self, post_seq):
        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        student_id = g.user_id
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        post_row = MealBoard.query.filter_by(post_seq=post_seq).first()
        if post_row is None:
            return {"message": "글을 찾을 수 없습니다."}, 404

        like_row = MealBoardLikes.query.filter_by(student=student, post_seq=post_seq).first()
        return {"data": {
            "post_seq": post_seq,
            "like": False if like_row is None else True
        }}, 200