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
from sqlalchemy import func


from app.scheduler import sched
from app.redis import rd
import datetime, time

class _MealBoard(Resource):
    @return_500_if_errors
    def get(self):
        args = request.args
        print(args)
        try:

            args = MealBoardGetListSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        post_rows = db.session.query(MealBoard, func.count(MealBoardLikes.like_seq).label("like_count")).outerjoin(
            MealBoardLikes,
            MealBoard.post_seq == MealBoardLikes.post_seq).filter(
            MealBoard.banned == False).group_by(MealBoard.post_seq).order_by(MealBoard.post_seq).limit(
            args["limit"]).offset(
            args["limit"] * args["page"]).all()

        print(post_rows[0])
        #
        # post_rows = MealBoard.query.filter_by(banned=False).limit(args["limit"]).offset(
        #     args["limit"] * args["page"]).all()

        if len(post_rows) == 0:
            return {
                       "message": "글을 찾을 수 없습니다."
                   }, 404

        return {
                   "data": [{
                       "postSeq": post_row.MealBoard.post_seq,
                       "title": post_row.MealBoard.title,
                       "post_date": str(post_row.MealBoard.post_date),
                       "image_url": post_row.MealBoard.image_url,
                       "like_count": post_row.like_count,
                       "views": post_row.MealBoard.views,
                   } for post_row in post_rows]
               }, 200

    @return_500_if_errors
    @login_required
    def post(self):
        student_id = g.user_id

        try:
            args = json.loads(request.form.get('jsonRequestData'))
        except Exception as e:
            print(request.form.get('jsonRequestData'))
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        # print(args)
        try:

            args = MealBoardSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        # print(args)

        image_file = request.files['imageFile']
        image_file_extension = os.path.splitext(image_file.filename)[1]
        if image_file_extension not in [".jpg", ".png", ".jpeg"]:
            return {"message": "이미지 파일만 업로드 가능합니다."}, 400

        print(image_file)
        print(image_file_extension)
        image = Image.open(image_file)

        def get_absoulute_path(path):
            script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
            rel_path = path
            abs_file_path = os.path.join(script_dir, rel_path)
            return abs_file_path

        image.save(get_absoulute_path("./temp/image.jpg"), quality=85, optimize=True)

        student, school = get_identify(student_id)
        lunch_meal_data = get_day_meal(school, args["menu_date"])

        bucket = firebase_admin.storage.bucket(name="meal-project-fa430.appspot.com", app=None)
        # bucket.put(image_file)
        blob = bucket.blob(f"user_images/meal/{student.nickname}_{uuid.uuid1()}{image_file_extension}")
        with open(get_absoulute_path("./temp/image.jpg"), "rb") as f:
            blob.upload_from_file(file_obj=f, content_type='image/jpeg')
            blob.make_public()

        image_url = blob.public_url

        post_row = MealBoard(
            school=school,
            student=student,
            menus=lunch_meal_data,
            image_url=image_url,
            menu_date=args["menu_date"],
            post_date=datetime.datetime.now(),
            title=args["title"],
            content=args["content"],
            banned=False,
        )
        db.session.add(post_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200


class _MealBoardMy(Resource):
    @return_500_if_errors
    @login_required
    def get(self):
        args = request.args
        print(args)
        try:

            args = MealBoardGetListSchema().load(args)
        except marshmallow.exceptions.ValidationError as e:
            print(e.messages)
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        student_id = g.user_id
        student, school = get_identify(student_id)

        post_rows = db.session.query(MealBoard, func.count(MealBoardLikes.like_seq).label("like_count")).outerjoin(
            MealBoardLikes,
            MealBoard.post_seq == MealBoardLikes.post_seq).filter(
            MealBoard.banned == False).filter(student=student).group_by(MealBoard.post_seq).order_by(MealBoard.post_seq).limit(
            args["limit"]).offset(
            args["limit"] * args["page"]).all()

        print(post_rows[0])
        #
        # post_rows = MealBoard.query.filter_by(banned=False).limit(args["limit"]).offset(
        #     args["limit"] * args["page"]).all()

        if len(post_rows) == 0:
            return {
                       "message": "글을 찾을 수 없습니다."
                   }, 404

        return {
                   "data": [{
                       "postSeq": post_row.MealBoard.post_seq,
                       "title": post_row.MealBoard.title,
                       "post_date": str(post_row.MealBoard.post_date),
                       "image_url": post_row.MealBoard.image_url,
                       "like_count": post_row.like_count,
                       "views": post_row.MealBoard.views
                   } for post_row in post_rows]
               }, 200




class _MealBoardDetail(Resource):

    @return_500_if_errors
    @login_required
    def get(self, post_seq):
        # post_seq번째 글만 가져옴

        student_id = g.user_id
        student, school = get_identify(student_id)

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
                       "views" : post_row.MealBoard.views,
                       "like_count": post_row.like_count,
                   }
               }, 200

    @return_500_if_errors
    @login_required
    def delete(self, post_seq):
        # 글 삭제
        student_id = g.user_id
        student, school = get_identify(student_id)
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


class _MealBoardLike(Resource):
    @return_500_if_errors
    @login_required
    def post(self, post_seq):
        student_id = g.user_id
        student, school = get_identify(student_id)
        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        post_row = MealBoard.query.filter_by(post_seq=post_seq).first()
        if post_row is None:
            return {"message" : "글을 찾을 수 없습니다."}, 404


        old_like_row = MealBoardLikes.query.filter_by(student=student, post_seq=post_seq).first()
        if old_like_row is not None:
            return {"message": "이미 좋아요 했습니다."}, 409

        like_row = MealBoardLikes(
            student=student,
            post_seq=post_seq,
            like_date=datetime.datetime.now()
        )

        db.session.add(like_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200

    @return_500_if_errors
    @login_required
    def delete(self, post_seq):
        student_id = g.user_id
        student, school = get_identify(student_id)
        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400

        post_row = MealBoard.query.filter_by(post_seq=post_seq).first()
        if post_row is None:
            return {"message" : "글을 찾을 수 없습니다."}, 404


        old_like_row = MealBoardLikes.query.filter_by(student=student, post_seq=post_seq).first()
        if old_like_row is None:
            return {"message": "좋아요를 하지 않았습니다."}, 409

        db.session.delete(old_like_row)
        db.session.commit()

        return {
                   "message": "정상적으로 처리되었습니다."
               }, 200


class _MealBoardLikeMy(Resource):

    @return_500_if_errors
    @login_required
    def get(self, post_seq):
        if post_seq is None or type(post_seq) != int:
            return {"message": "파라미터 값이 유효하지 않습니다."}, 400
        student_id = g.user_id
        student, school = get_identify(student_id)

        post_row = MealBoard.query.filter_by(post_seq=post_seq).first()
        if post_row is None:
            return {"message": "글을 찾을 수 없습니다."}, 404

        like_row = MealBoardLikes.query.filter_by(student=student, post_seq=post_seq).first()
        return {"data": {
            "post_seq": post_seq,
            "like": False if like_row is None else True
        }}, 200

