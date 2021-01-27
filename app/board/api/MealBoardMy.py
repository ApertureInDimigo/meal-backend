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


class MealBoardMy(Resource):
    @return_500_if_errors
    @login_required
    def get(self):

        student_id = g.user_id
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        args = request.args
        print(args)
        try:

            args = MealBoardGetListSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        if args["limit"] * (args["page"] - 1) < 0:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        post_rows = db.session.query(MealBoard, func.count(MealBoardLikes.like_seq).label("like_count")).outerjoin(
            MealBoardLikes,
            MealBoard.post_seq == MealBoardLikes.post_seq).filter(
            MealBoard.banned == False).filter(MealBoard.student == student).group_by(MealBoard.post_seq).order_by(
            desc(MealBoard.post_seq)).limit(
            args["limit"]).offset(
            args["limit"] * (args["page"] - 1)).all()

        if len(post_rows) == 0:
            return {
                       "message": "글을 찾을 수 없습니다."
                   }, 404

        return {
                   "data": [{
                       "nickname": post_row.MealBoard.student.nickname,
                       "postSeq": post_row.MealBoard.post_seq,
                       "title": post_row.MealBoard.title,
                       "post_date": str(post_row.MealBoard.post_date),
                       "image_url": post_row.MealBoard.image_url,
                       "like_count": post_row.like_count,
                       "views": post_row.MealBoard.views,
                   } for post_row in post_rows]
               }, 200
