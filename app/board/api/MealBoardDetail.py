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


class MealBoardDetail(Resource):

    @return_500_if_errors
    @login_required
    def get(self, post_seq):
        # post_seq번째 글만 가져옴

        student_id = g.user_id
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401

        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        post_row = db.session.query(MealBoard, func.count(MealBoardLikes.like_seq).label("like_count")).outerjoin(
            MealBoardLikes,
            MealBoard.post_seq == MealBoardLikes.post_seq).filter(
            MealBoard.banned == False).filter(MealBoard.post_seq == post_seq).group_by(MealBoard.post_seq).first()

        if post_row is None:
            return {
                       "message": "글을 찾을 수 없습니다."
                   }, 404

        student_seq = student.student_seq
        print("@", rd.scan_iter(match="pviews:*"))
        # for key in rd.scan_iter(match="pviews:*"):
        # print("@@@",key)

        if not rd.exists(f'pviews:{post_seq}-{student_seq}'):
            rd.sadd(f'views:{post_seq}', student_seq)

        # print(rd.keys)
        for key in rd.scan_iter(match="views:*"):
            print(rd.smembers(key))

        return {
                   "data": {
                       "postSeq": post_row.MealBoard.post_seq,
                       "title": post_row.MealBoard.title,
                       "content": post_row.MealBoard.content,
                       "menus": post_row.MealBoard.menus,
                       "menu_date": str(post_row.MealBoard.menu_date),
                       "post_date": str(post_row.MealBoard.post_date),
                       "image_url": post_row.MealBoard.image_url,
                       "views": post_row.MealBoard.views,
                       "like_count": post_row.like_count,
                   }
               }, 200

    @return_500_if_errors
    @login_required
    def delete(self, post_seq):
        # 글 삭제
        student_id = g.user_id
        student, school = get_identify() or (None, None)
        if student is None: return {"message": "올바르지 않은 회원 정보입니다."}, 401
        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 40

        post_row = MealBoard.query.filter_by(student=student, post_seq=post_seq).first()
        if post_row is None:
            return {"message": "글을 찾을 수 없습니다."}, 404
        print(post_row)
        db.session.delete(post_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200